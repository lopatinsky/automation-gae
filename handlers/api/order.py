# coding:utf-8
import logging
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext.ndb import GeoPt, Key
from config import config
from handlers.api.base import ApiHandler
import json
from datetime import datetime, timedelta
from methods import alfa_bank, empatika_promos, orders, empatika_wallet, email, paypal
from methods.orders.validation import validate_order, get_first_error
from methods.map import get_houses_by_address
from methods.orders.precheck import check_order_id, set_client_info, get_venue_by_address, get_delivery_time_minutes
from models import Client, CARD_PAYMENT_TYPE, Order, NEW_ORDER, Venue, CANCELED_BY_CLIENT_ORDER, IOS_DEVICE, \
    PaymentType, STATUS_AVAILABLE, READY_ORDER, CREATING_ORDER, SELF, IN_CAFE, GiftMenuItem, GiftPositionDetails, Address, \
    PAYPAL_PAYMENT_TYPE
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

        delivery_type = int(response_json.get('delivery_type'))

        delivery_venue = None
        address = response_json.get('address')
        if address:
            address_home = address['address']
            if not address['address']['home']:
                candidates = get_houses_by_address(address_home['city'], address_home['street'], address_home['home'])
                if candidates:
                    flat = address['address']['flat']
                    address = candidates[0]
                    address['address']['flat'] = flat
            delivery_venue = get_venue_by_address(address)

        if delivery_type in [SELF, IN_CAFE]:
            venue_id = response_json.get('venue_id')
            if not venue_id:
                return self.render_error(u"Произошла ошибка. Попробуйте выбрать заново выбрать кофейню.")
            venue_id = int(venue_id)
            venue = Venue.get_by_id(venue_id)
            if not venue:
                return self.render_error("")
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

        delivery_time_minutes = response_json.get('delivery_time')
        delivery_slot = response_json.get('delivery_slot')
        if venue and delivery_slot and not delivery_time_minutes:
            success, delivery_time_minutes = get_delivery_time_minutes(venue, delivery_type, delivery_slot)
            if not success:
                return self.render_error(u'Неправильно выбран слот для времени')
        if delivery_time_minutes is not None:
            delivery_time = datetime.utcnow() + timedelta(minutes=delivery_time_minutes)
        else:
            delivery_time = None
        request_total_sum = response_json.get("total_sum")

        client_id, client = set_client_info(response_json.get('client'))
        if not client:
            return self.render_error("")

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
                                               response_json['payment'],
                                               venue, address, delivery_time_minutes, delivery_slot, delivery_type, True)
            if not validation_result['valid']:
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

            if delivery_slot:
                delivery_slot_name = delivery_slot.get('name')
            else:
                delivery_slot_name = None

            self.order = Order(
                id=order_id, client_id=client_id, venue_id=venue_id, total_sum=total_sum, coordinates=coordinates,
                comment=comment, status=CREATING_ORDER, device_type=device_type, delivery_time=delivery_time,
                payment_type_id=payment_type_id, promos=promo_list, items=item_keys, wallet_payment=wallet_payment,
                item_details=item_details, delivery_type=delivery_type, delivery_slot=delivery_slot_name,
                address=address_obj)
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
                success, info = paypal.pay(order_id, payment_amount / 100.0, client.paypal_refresh_token, correlation_id)

                if success:
                    self.order.payment_id = info
                    self.order.put()
                else:
                    return self.render_error(u"Не удалось произвести оплату. " + (info or ''))

            gift_details = []
            for gift in response_json.get('gifts', []):
                gift_item = GiftMenuItem.get_by_id(int(gift['item_id']))
                activation_dict = empatika_promos.activate_promo(client.key.id(), gift_item.promo_id, 1)
                gift_details.append(GiftPositionDetails(gift=gift_item.key,
                                                        activation_id=activation_dict['activation']['id']))
            self.order.gift_details = gift_details

            client.put()
            self.order.status = NEW_ORDER

            # it is used for creating db for promos
            validate_order(client, response_json['items'], response_json.get('gifts', []), response_json['payment'],
                           venue, address, delivery_time_minutes, delivery_slot, delivery_type, False, self.order)
            self.order.put()

            taskqueue.add(url='/task/check_order_success', params={'order_id': order_id},
                          countdown=SECONDS_WAITING_BEFORE_SMS)

            memcache.delete(self.cache_key)

            self.response.status_int = 201
            self.render_json({'order_id': order_id})
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
                # return money
                if order.has_card_payment:
                    return_result = alfa_bank.reverse(order.payment_id)
                    if str(return_result.get('errorCode', 0)) != '0':
                        logging.error("payment return failed")
                        self.abort(400)
                elif order.has_paypal_payment:
                    success, error = paypal.void(order.payment_id)
                    if not success:
                        self.abort(400)
                for gift_detail in order.gift_details:
                    try:
                        empatika_promos.cancel_activation(gift_detail.activation_id)
                    except empatika_promos.EmpatikaPromosError as e:
                        logging.exception(e)
                        self.abort(400)

                if order.wallet_payment > 0:
                    try:
                        empatika_wallet.reverse(order.client_id, order_id)
                    except empatika_wallet.EmpatikaWalletError as e:
                        logging.exception(e)
                        email.send_error("payment", "Wallet reversal failed", str(e))
                        # main payment reversed -- do not abort

                order.status = CANCELED_BY_CLIENT_ORDER
                order.return_datetime = datetime.utcnow()
                order.put()

                self.render_json({
                    'error': 0,
                    'order_id': order.key.id()
                })
                logging.info(u'заказ %d отменен' % order_id)
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
            delivery_venue = get_venue_by_address(address)

        if delivery_type in [SELF, IN_CAFE]:
            venue_id = self.request.get_range('venue_id')
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

        delivery_time = self.request.get('delivery_time')
        delivery_slot = self.request.get('delivery_slot')
        if delivery_slot:
            delivery_slot = json.loads(delivery_slot)
        if delivery_time:
            delivery_time = int(delivery_time)
        if venue and delivery_slot and not delivery_time:
            success, delivery_time = get_delivery_time_minutes(venue, delivery_type, delivery_slot)
            if not success:
                self.abort(501)

        items = json.loads(self.request.get('items'))
        if self.request.get('gifts'):
            gifts = json.loads(self.request.get('gifts'))
        else:
            gifts = []

        result = orders.validate_order(client, items, gifts, payment_info, venue, address, delivery_time, delivery_slot,
                                       delivery_type)
        self.render_json(result)