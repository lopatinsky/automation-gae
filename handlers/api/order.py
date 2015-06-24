# coding:utf-8
import logging
from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb
from webapp2_extras import security
from google.appengine.ext.ndb import GeoPt, Key
from config import config
from handlers.api.base import ApiHandler
import json
from datetime import datetime, timedelta
from handlers.web_admin.web.company.delivery.orders import order_items_values
from methods import alfa_bank, empatika_promos, orders, empatika_wallet, paypal
from methods.orders.validation import validate_order, get_first_error
from methods.orders.cancel import cancel_order
from methods.twilio import send_sms
from methods.email_mandrill import send_email
from methods.orders.precheck import check_order_id, set_client_info, get_venue_and_zone_by_address,\
    check_items_and_gifts, get_delivery_time, validate_address
from google.appengine.api import taskqueue
from models import DeliverySlot, STATUS_AVAILABLE, PaymentType, Order, Venue, Address, Client
from models.client import IOS_DEVICE
from models.order import READY_ORDER, NEW_ORDER, CREATING_ORDER, CANCELED_BY_CLIENT_ORDER, CONFUSED_CHOICES, \
    CONFUSED_OTHER
from models.payment_types import CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE, PAYMENT_TYPE_MAP
from models.venue import SELF, IN_CAFE, DELIVERY_MAP, DELIVERY, PICKUP
from handlers.email_api.order import POSTPONE_MINUTES

SECONDS_WAITING_BEFORE_SMS = 15

EMAIL_FROM = 'noreply-order@ru-beacon.ru'


class OrderHandler(ApiHandler):
    order = None

    def render_error(self, description, title=u"Ошибка"):
        self.response.set_status(400)
        logging.warning("order render_error: %s" % description)
        self.render_json({
            "title": title,
            "description": description
        })
        if self.order:
            self.order.key.delete()

    def post(self):
        response_json = json.loads(self.request.get('order'))
        order_id = response_json.get('order_id')
        if order_id:
            order_id = int(order_id)
        success, order_id = check_order_id(order_id)
        if not success:
            self.abort(409)

        if not config.IN_PRODUCTION:
            return self.render_error(u'Приложение работает в тестовом режиме, оставайтесь с нами, мы скоро запустимся!')

        success = check_items_and_gifts(response_json['items'], response_json.get('gifts', []))
        if not success:
            return self.render_error(u'Выберите что-нибудь')

        delivery_type = int(response_json.get('delivery_type'))

        venue = None
        delivery_zone = None
        address = response_json.get('address')
        if delivery_type in [SELF, IN_CAFE]:
            venue_id = response_json.get('venue_id')
            if not venue_id:
                return self.render_error(u"Произошла ошибка. Попробуйте выбрать заново выбрать кофейню.")
            venue_id = int(venue_id)
            venue = Venue.get_by_id(venue_id)
            if not venue:
                return self.render_error(u"Кофейня не найдена")
        elif delivery_type in [DELIVERY, PICKUP]:
            if address:
                address = validate_address(address)
                venue, delivery_zone = get_venue_and_zone_by_address(address)
        if not venue:
            return self.render_error(u'Недостаточно информации для обработки заказа')
        else:
            venue_id = venue.key.id()

        if 'coordinates' in response_json:
            coordinates = GeoPt(response_json['coordinates'])
        else:
            coordinates = None

        comment = response_json['comment']
        device_type = response_json.get('device_type', IOS_DEVICE)

        delivery_slot_id = response_json.get('delivery_slot_id')
        if delivery_slot_id:
            delivery_slot_id = int(delivery_slot_id)
            delivery_slot = DeliverySlot.get_by_id(delivery_slot_id)
            if not delivery_slot:
                return self.render_error(u'Неправильный формат времени')
        else:
            delivery_slot = None
            delivery_slot_id = None

        delivery_time_minutes = response_json.get('delivery_time')    # used for old versions todo: remove
        if delivery_time_minutes:                                     # used for old versions todo: remove
            delivery_time_minutes = int(delivery_time_minutes)        # used for old versions todo: remove
        delivery_time_picker = response_json.get('time_picker_value')

        delivery_time = get_delivery_time(delivery_time_picker, venue, delivery_slot, delivery_time_minutes)
        if not delivery_time:
            return self.render_error(u'Неправильный формат времени')

        request_total_sum = response_json.get("total_sum")

        client_id, client = set_client_info(response_json.get('client'))
        if not client:
            return self.render_error(u'Неудачная попытка авторизации. Попробуйте позже')

        payment_type_id = response_json['payment']['type_id']
        payment_type = PaymentType.get_by_id(str(payment_type_id))

        wallet_payment = response_json['payment'].get('wallet_payment', 0.0)

        if payment_type.status == STATUS_AVAILABLE:

            item_keys = [Key('MenuItem', int(item['item_id'])) for item in response_json['items']]

            after_error = response_json.get("after_error")
            if after_error:
                five_mins_ago = datetime.utcnow() - timedelta(minutes=3)
                previous_order = Order.query(Order.client_id == client_id,
                                             Order.status.IN([READY_ORDER, NEW_ORDER]),
                                             Order.date_created >= five_mins_ago).get()
                if previous_order and sorted(previous_order.items) == sorted(item_keys):
                    return self.render_error(u"Этот заказ уже зарегистрирован в системе, проверьте историю заказов.")

            validation_result = validate_order(client,
                                               response_json['items'],
                                               response_json.get('gifts', []),
                                               response_json.get('order_gifts', []),
                                               response_json.get('cancelled_order_gifts', []),
                                               response_json['payment'],
                                               venue, address, delivery_time, delivery_slot, delivery_type,
                                               delivery_zone, True)
            if not validation_result['valid']:
                logging.warning('Fail in validation')
                return self.render_error(get_first_error(validation_result))

            total_sum = validation_result['total_sum']
            if request_total_sum and int(total_sum * 100) != int(request_total_sum * 100):
                return self.render_error(u"Сумма заказа была пересчитана", u"")
            if wallet_payment and int(wallet_payment * 100) != int(validation_result['max_wallet_payment'] * 100):
                return self.render_error(u"Сумма оплаты баллами была пересчитана", u"")

            item_details = validation_result["details"]
            promo_list = [ndb.Key('Promo', promo['id']) for promo in validation_result["promos"]]

            if address:
                address_args = {
                    'lat': float(address['coordinates']['lat']) if address['coordinates']['lat'] else None,
                    'lon': float(address['coordinates']['lon']) if address['coordinates']['lon'] else None
                }
                address_args.update(address['address'])
                address_obj = Address(**address_args)
            else:
                address_obj = None

            self.order = Order(
                id=order_id, client_id=client_id, venue_id=venue_id, total_sum=total_sum, coordinates=coordinates,
                comment=comment, status=CREATING_ORDER, device_type=device_type, delivery_time=delivery_time,
                delivery_time_str=validation_result['delivery_time'], payment_type_id=payment_type_id,
                promos=promo_list, items=item_keys, wallet_payment=wallet_payment, item_details=item_details,
                delivery_type=delivery_type, delivery_slot_id=delivery_slot_id, address=address_obj,
                delivery_zone=delivery_zone.key if delivery_zone else None,
                user_agent=self.request.headers["User-Agent"])
            self.order.put()

            if wallet_payment > 0:
                empatika_wallet.pay(client_id, order_id, int(wallet_payment * 100))

            payment_amount = int((total_sum - wallet_payment) * 100)

            if payment_type_id == CARD_PAYMENT_TYPE and payment_amount > 0:
                binding_id = response_json['payment']['binding_id']
                alpha_client_id = response_json['payment']['client_id']
                return_url = response_json['payment']['return_url']

                success, result = alfa_bank.create_simple(payment_amount, order_id, return_url, alpha_client_id)
                if not success:
                    error = result
                else:
                    self.order.payment_id = result
                    self.order.put()
                    success, error = alfa_bank.hold_and_check(self.order.payment_id, binding_id)
                if not success:
                    if wallet_payment > 0:
                        empatika_wallet.reverse(client_id, order_id)
                    return self.render_error(u"Не удалось произвести оплату. " + (error or ''))
            elif payment_type_id == PAYPAL_PAYMENT_TYPE and payment_amount > 0:
                correlation_id = response_json['payment']['correlation_id']
                success, info = paypal.authorize(order_id, payment_amount / 100.0, client.paypal_refresh_token,
                                                 correlation_id)

                if success:
                    self.order.payment_id = info
                    self.order.put()
                else:
                    return self.render_error(u"Не удалось произвести оплату. " + (info or ''))

            gift_details = []
            for gift_detail in validation_result['gift_details']:
                gift_item = gift_detail.gift.get()
                activation_dict = empatika_promos.activate_promo(client.key.id(), gift_item.promo_id, 1)
                gift_detail.activation_id = activation_dict['activation']['id']
                gift_details.append(gift_detail)
            self.order.gift_details = gift_details

            client.put()
            self.order.status = NEW_ORDER

            # it is used for creating db for promos
            validate_order(client, response_json['items'], response_json.get('gifts', []),
                           response_json.get('order_gifts', []), response_json.get('cancelled_order_gifts', []),
                           response_json['payment'], venue, address, delivery_time, delivery_slot, delivery_type,
                           delivery_zone, False, self.order)
            self.order.put()

            # use delivery phone and delivery emails for all delivery types
            text = u'Новый заказ №%s поступил в систему из мобильного приложения' % self.order.key.id()
            if config.DELIVERY_PHONE:
                send_sms([config.DELIVERY_PHONE], text)
            if config.DELIVERY_EMAILS:
                item_values = order_items_values(self.order)
                item_values['venue'] = venue
                item_values['delivery_type_str'] = DELIVERY_MAP[self.order.device_type]
                self.order.payment_type_str = PAYMENT_TYPE_MAP[self.order.payment_type_id]
                if config.EMAIL_REQUESTS:
                    self.order.email_key_done = security.generate_random_string(entropy=256)
                    self.order.email_key_cancel = security.generate_random_string(entropy=256)
                    self.order.email_key_postpone = security.generate_random_string(entropy=256)
                    self.order.put()
                    base_url = urlparse(self.request.url).hostname
                    item_values['done_url'] = 'http://%s/email/order/close?key=%s' % (base_url, self.order.email_key_done)
                    item_values['cancel_url'] = 'http://%s/email/order/cancel?key=%s' % (base_url, self.order.email_key_cancel)
                    item_values['postpone_url'] = 'http://%s/email/order/postpone?key=%s' % (base_url, self.order.email_key_postpone)
                    item_values['minutes'] = POSTPONE_MINUTES
                for email in config.DELIVERY_EMAILS:
                    send_email(EMAIL_FROM, email, text, self.jinja2.render_template('/company/delivery/items.html', **item_values))

            taskqueue.add(url='/task/check_order_success', params={'order_id': order_id},
                          countdown=SECONDS_WAITING_BEFORE_SMS)

            self.response.status_int = 201
            self.render_json({
                'order_id': order_id,
                'delivery_time': validation_result['delivery_time'],
                'delivery_slot_name': validation_result['delivery_slot_name']
            })
        else:
            self.render_error(u"Выбранный способ оплаты недоступен.")


class RegisterOrderHandler(ApiHandler):
    def get(self):
        self.render_json({'order_id': Order.generate_id()})


class ReturnOrderHandler(ApiHandler):
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        elif order.status != NEW_ORDER:
            self.response.status_int = 412
            self.render_json({
                'error': 1,
                'description': u'Заказ уже выдан или отменен'
            })
        else:
            now = datetime.utcnow()
            if now - order.date_created < timedelta(seconds=config.CANCEL_ALLOWED_WITHIN) or \
                    order.delivery_time - now > timedelta(minutes=config.CANCEL_ALLOWED_BEFORE):
                success = cancel_order(order, CANCELED_BY_CLIENT_ORDER, namespace_manager.get_namespace(),
                                       with_push=False)
                if success:
                    reason_id = self.request.get('reason_id')
                    if reason_id:
                        reason_id = int(reason_id)
                        if reason_id in CONFUSED_CHOICES:
                            order.cancel_reason = reason_id
                        if reason_id == CONFUSED_OTHER:
                            order.cancel_reason_text = self.request.get('reason_text')
                        order.put()
                    self.render_json({
                        'error': 0,
                        'order_id': order.key.id()
                    })
                    logging.info(u'заказ %d отменен' % order_id)
                else:
                    self.response.status_int = 422
                    self.render_json({
                        'error': 1,
                        'description': u'При отмене возникла ошибка'  # todo: change this text
                    })
            else:
                self.response.status_int = 412
                self.render_json({
                    'error': 1,
                    'description': u'Отмена заказа невозможна, так как до его исполнения осталось менее %s минут.' %
                                   config.CANCEL_ALLOWED_BEFORE
                })


class AddReturnCommentHandler(ApiHandler):
    def post(self):
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        if order.status != CANCELED_BY_CLIENT_ORDER:
            self.abort(400)

        text = self.request.get('text')
        order.return_comment = text
        order.put()
        self.render_json({})


#  all required fields should invoke 400
#  all errors should be catch in orders.validate_order
## address can be None => send error
## payment can be None => send error
class CheckOrderHandler(ApiHandler):
    def post(self):
        logging.info(self.request.POST)

        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)

        delivery_type = int(self.request.get('delivery_type'))

        venue = None
        delivery_zone = None
        address = self.request.get('address')

        if delivery_type in [SELF, IN_CAFE]:
            venue_id = self.request.get_range('venue_id')
            if not venue_id or venue_id == -1:
                self.abort(400)
            venue = Venue.get_by_id(venue_id)
            if not venue:
                self.abort(400)
        elif delivery_type in [DELIVERY, PICKUP]:
            if address:
                address = json.loads(address)
                address = validate_address(address)
            venue, delivery_zone = get_venue_and_zone_by_address(address)
        if not venue:  # not enough fields for catch venue
            self.abort(400)

        raw_payment_info = self.request.get('payment')
        payment_info = None
        if raw_payment_info:
            payment_info = json.loads(raw_payment_info)
            if (not payment_info.get('type_id') and payment_info.get('type_id') != 0) or \
                            payment_info.get('type_id') == -1:
                payment_info = None

        delivery_slot_id = self.request.get('delivery_slot_id')
        if delivery_slot_id:
            delivery_slot_id = int(delivery_slot_id)
            delivery_slot = DeliverySlot.get_by_id(delivery_slot_id)
        else:
            delivery_slot = None

        delivery_time_minutes = self.request.get('delivery_time')     # used for old versions todo: remove
        if delivery_time_minutes:                                     # used for old versions todo: remove
            delivery_time_minutes = int(delivery_time_minutes)        # used for old versions todo: remove
        delivery_time_picker = self.request.get('time_picker_value')

        delivery_time = get_delivery_time(delivery_time_picker, venue, delivery_slot, delivery_time_minutes)
        if not delivery_time:
            self.abort(400)

        items = json.loads(self.request.get('items'))
        if self.request.get('gifts'):
            gifts = json.loads(self.request.get('gifts'))
        else:
            gifts = []
        if self.request.get('order_gifts'):
            order_gifts = json.loads(self.request.get('order_gifts'))
        else:
            order_gifts = []
        if self.request.get('cancelled_order_gifts'):
            cancelled_order_gifts = json.loads(self.request.get('cancelled_order_gifts'))
        else:
            cancelled_order_gifts = []
        result = orders.validate_order(client, items, gifts, order_gifts, cancelled_order_gifts, payment_info, venue,
                                       address, delivery_time, delivery_slot, delivery_type, delivery_zone)
        self.render_json(result)