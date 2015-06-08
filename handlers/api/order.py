# coding:utf-8
import logging
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext.ndb import GeoPt, Key
from config import config
from handlers.api.base import ApiHandler
import json
from datetime import datetime, timedelta
from handlers.web_admin.web.company.delivery.orders import order_items_values
from methods import alfa_bank, empatika_promos, orders, empatika_wallet, paypal
from methods.orders.validation import validate_order, get_first_error
from methods.map import get_houses_by_address
from methods.orders.cancel import cancel_order
from methods.twilio import send_sms
from methods.email_mandrill import send_email
from methods.orders.precheck import check_order_id, set_client_info, get_venue_and_zone_by_address,\
    check_items_and_gifts, get_delivery_time
from models import Client, CARD_PAYMENT_TYPE, Order, NEW_ORDER, Venue, CANCELED_BY_CLIENT_ORDER, IOS_DEVICE, \
    PaymentType, STATUS_AVAILABLE, READY_ORDER, CREATING_ORDER, SELF, IN_CAFE, Address, DeliverySlot, \
    PAYPAL_PAYMENT_TYPE, CONFUSED_CHOICES, CONFUSED_OTHER
from google.appengine.api import taskqueue

SECONDS_WAITING_BEFORE_SMS = 15


class OrderHandler(ApiHandler):
    cache_key = None
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
        memcache.delete(self.cache_key)

    def post(self):
        response_json = json.loads(self.request.get('order'))
        order_id = int(response_json['order_id'])
        success, cache_key = check_order_id(order_id)
        if not success:
            self.abort(409)
        else:
            self.cache_key = cache_key

        if not config.IN_PRODUCTION:
            return self.render_error(u'Приложение работает в тестовом режиме, оставайтесь с нами, мы скоро запустимся!')

        success = check_items_and_gifts(response_json['items'], response_json.get('gifts', []))
        if not success:
            self.render_error(u'Выберите что-нибудь')

        delivery_type = int(response_json.get('delivery_type'))

        delivery_venue = None
        delivery_zone = None
        address = response_json.get('address')
        if address:
            address_home = address['address']
            if not address['address']['home']:
                candidates = get_houses_by_address(address_home['city'], address_home['street'], address_home['home'])
                if candidates:
                    flat = address['address']['flat']
                    address = candidates[0]
                    address['address']['flat'] = flat
            delivery_venue, delivery_zone = get_venue_and_zone_by_address(address)

        if delivery_type in [SELF, IN_CAFE]:
            venue_id = response_json.get('venue_id')
            if not venue_id:
                return self.render_error(u"Произошла ошибка. Попробуйте выбрать заново выбрать кофейню.")
            venue_id = int(venue_id)
            venue = Venue.get_by_id(venue_id)
            if not venue:
                return self.render_error(u"Кофейня не найдена")
        else:
            if delivery_venue:
                venue_id = delivery_venue.key.id()
                venue = delivery_venue
            else:
                venue_id = None
                venue = None

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
                delivery_zone=delivery_zone.key)
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
                for email in config.DELIVERY_EMAILS:
                    send_email(email, email, text, self.jinja2.render_template('/company/delivery/items.html',
                                                                               **order_items_values(self.order)))

            taskqueue.add(url='/task/check_order_success', params={'order_id': order_id},
                          countdown=SECONDS_WAITING_BEFORE_SMS)

            memcache.delete(self.cache_key)

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


class StatusHandler(ApiHandler):
    def post(self):
        response_json = json.loads(self.request.get('orders'))
        orders = []
        for order_id in response_json['orders']:
            order = Order.get_by_id(int(order_id))
            if order:
                orders.append(order)
        self.render_json({'status': [order.status_dict() for order in orders]})


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
                success = cancel_order(order, CANCELED_BY_CLIENT_ORDER, with_push=False)
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


class CheckOrderHandler(ApiHandler):
    def post(self):
        logging.info(self.request.POST)

        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)

        delivery_type = int(self.request.get('delivery_type'))

        delivery_venue = None
        delivery_zone = None
        address = self.request.get('address')
        if address:
            address = json.loads(address)
            address_home = address['address']
            if not address['address']['home']:
                candidates = get_houses_by_address(address_home['city'], address_home['street'], address_home['home'])
                if candidates:
                    flat = address['address']['flat']
                    address = candidates[0]
                    address['address']['flat'] = flat
            delivery_venue, delivery_zone = get_venue_and_zone_by_address(address)

        if delivery_type in [SELF, IN_CAFE]:
            venue_id = self.request.get_range('venue_id')
            if not venue_id or venue_id == -1:
                self.abort(400)
            venue = Venue.get_by_id(venue_id)
            if not venue:
                self.abort(400)
        else:
            venue = delivery_venue

        raw_payment_info = self.request.get('payment')
        try:
            payment_info = json.loads(raw_payment_info)
        except ValueError:
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