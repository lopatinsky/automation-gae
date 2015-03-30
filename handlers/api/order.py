# coding:utf-8
import logging
from google.appengine.api import memcache
from google.appengine.ext.ndb import GeoPt, Key
from config import config
from handlers.api.base import ApiHandler
import json
import re
from datetime import datetime, timedelta
from methods import alfa_bank, empatika_promos, orders, versions, empatika_wallet
from methods.orders.validation import validate_order, get_first_error
from models import Client, MenuItem, CARD_PAYMENT_TYPE, Order, NEW_ORDER, Venue, CANCELED_BY_CLIENT_ORDER, IOS_DEVICE, \
    BONUS_PAYMENT_TYPE, PaymentType, STATUS_AVAILABLE, READY_ORDER, CREATING_ORDER, SingleModifier, GroupModifier, \
    WALLET_PAYMENT_TYPE
from google.appengine.api import taskqueue
from methods.email_mandrill import send_email
from webapp2_extras import jinja2

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
        #TODO errors handling
        response_json = json.loads(self.request.get('order'))
        order_id = int(response_json['order_id'])
        # check if order exists in DB or currently adding it
        self.cache_key = "order_%s" % order_id
        if Order.get_by_id(order_id) or not memcache.add(self.cache_key, 1):
            self.abort(409)

        venue_id = response_json.get('venue_id')
        if not venue_id:
            return self.render_error(u"Произошла ошибка. Попробуйте выбрать заново выбрать кофейню.")
        venue_id = int(venue_id)

        venue = Venue.get_by_id(venue_id)
        if not venue:
            return self.render_error("")

        if 'coordinates' in response_json:
            coordinates = GeoPt(response_json['coordinates'])
        else:
            coordinates = None
        comment = response_json['comment']
        device_type = response_json.get('device_type', IOS_DEVICE)
        delivery_time_minutes = response_json['delivery_time']
        delivery_time = datetime.utcnow() + timedelta(minutes=delivery_time_minutes)
        request_total_sum = response_json.get("total_sum")
        client_id = int(response_json['client']['id'])

        client = Client.get_by_id(int(client_id))
        name = response_json['client']['name'].split(None, 1)
        client_name = name[0]
        client_surname = name[1] if len(name) > 1 else ""
        client_tel = re.sub("[^0-9]", "", response_json['client']['phone'])
        client_email = response_json['client'].get('email')
        if client.name != client_name or client.surname != client_surname or client.tel != client_tel \
                or client.email != client_email:
            client.name = client_name
            client.surname = client_surname
            client.tel = client_tel
            client.email = client_email
            client.put()

        payment_type_id = response_json['payment']['type_id']
        payment_type = PaymentType.get_by_id(str(payment_type_id))

        if payment_type.status == STATUS_AVAILABLE:

            item_keys = [Key('MenuItem', int(item['item_id'])) for item in response_json['items']]

            after_error = response_json.get("after_error")
            if after_error:
                five_mins_ago = datetime.utcnow() - timedelta(minutes=3)
                previous_order = Order.query(Order.client_id == client_id,
                                             Order.status.IN([READY_ORDER, NEW_ORDER]),
                                             Order.date_created >= five_mins_ago).get()
                if previous_order and sorted(previous_order.items) == sorted(item_keys):
                    self.render_error(u"Этот заказ уже зарегистрирован в системе, проверьте историю заказов.")
                    return

            validation_result = validate_order(client, response_json['items'], response_json['payment'], venue,
                                               delivery_time_minutes, True)
            if not validation_result['valid']:
                return self.render_error(get_first_error(validation_result))

            total_sum = validation_result['total_sum']
            if request_total_sum and total_sum != request_total_sum:
                return self.render_error(u"Сумма заказа была пересчитана", u"")

            item_details = validation_result["details"]
            promo_list = [promo['id'] for promo in validation_result["promos"]]

            self.order = Order(
                id=order_id, client_id=client_id, venue_id=venue_id, total_sum=total_sum, coordinates=coordinates,
                comment=comment, status=CREATING_ORDER, device_type=device_type, delivery_time=delivery_time,
                payment_type_id=payment_type_id, promos=promo_list, items=item_keys,
                item_details=item_details)
            self.order.put()

            if payment_type_id == CARD_PAYMENT_TYPE:
                binding_id = response_json['payment']['binding_id']
                alpha_client_id = response_json['payment']['client_id']
                return_url = response_json['payment']['return_url']

                success, result = alfa_bank.create_simple(total_sum, order_id, return_url, alpha_client_id)
                if not success:
                    error = result
                else:
                    self.order.payment_id = result
                    self.order.put()
                    success, error = alfa_bank.hold_and_check(self.order.payment_id, binding_id)
                if not success:
                    return self.render_error(u"Не удалось произвести оплату. " + (error or ''))

            if payment_type_id == WALLET_PAYMENT_TYPE:
                empatika_wallet.pay(client_id, order_id, total_sum)

            client.put()
            self.order.status = NEW_ORDER
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
                if order.payment_type_id == CARD_PAYMENT_TYPE:
                    return_result = alfa_bank.reverse(order.payment_id)
                    if str(return_result.get('errorCode', 0)) != '0':
                        logging.error("payment return failed")
                        self.abort(400)
                elif order.payment_type_id == BONUS_PAYMENT_TYPE:
                    try:
                        empatika_promos.cancel_activation(order.payment_id)
                    except empatika_promos.EmpatikaPromosError as e:
                        logging.exception(e)
                        self.abort(400)
                elif order.payment_type_id == WALLET_PAYMENT_TYPE:
                    try:
                        empatika_wallet.reverse(order.client_id, order_id)
                    except empatika_wallet.EmpatikaWalletError as e:
                        logging.exception(e)
                        self.abort(400)

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

        venue_id = self.request.get_range('venue_id')
        try:
            venue = Venue.get_by_id(venue_id)
        except:
            venue = None

        raw_payment_info = self.request.get('payment')
        try:
            payment_info = json.loads(raw_payment_info)
        except ValueError:
            payment_info = None

        delivery_time = self.request.get_range('delivery_time')
        items = json.loads(self.request.get('items'))

        result = orders.validate_order(client, items, payment_info, venue, delivery_time)
        self.render_json(result)
