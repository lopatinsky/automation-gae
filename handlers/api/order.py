# coding:utf-8
import logging
from google.appengine.api import memcache
from google.appengine.ext.ndb import GeoPt
from config import config
from handlers.api.base import ApiHandler
import json
from time import time as time_time
import re
from datetime import datetime, timedelta
from methods import alfa_bank, sms, push, empatika_promos, orders
from models import Client, MenuItem, CARD_PAYMENT_TYPE, Order, NEW_ORDER, Venue, CANCELED_BY_CLIENT_ORDER, IOS_DEVICE, \
    BONUS_PAYMENT_TYPE, PaymentType, STATUS_AVAILABLE

__author__ = 'ilyazorin'


class OrderHandler(ApiHandler):

    def post(self):
        #TODO errors handling
        response_json = json.loads(self.request.get('order'))
        order_id = int(response_json['order_id'])
        # check if order exists in DB or currently adding it
        cache_key = "order_%s" % order_id
        if Order.get_by_id(order_id) or not memcache.add(cache_key, 1):
            memcache.delete(cache_key)
            self.abort(409)

        venue_id = int(response_json['venue_id'])
        venue = Venue.get_by_id(venue_id)
        if not venue.active:
            memcache.delete(cache_key)
            self.abort(410)
        if not venue.is_open():
            memcache.delete(cache_key)
            self.error(400)
            self.render_json({
                "description": u"Эта кофейня сейчас закрыта."
            })
            return

        if 'coordinates' in response_json:
            coordinates = GeoPt(response_json['coordinates'])
        else:
            coordinates = None
        comment = response_json['comment']
        device_type = response_json.get('device_type', IOS_DEVICE)
        delivery_time = datetime.utcnow() + timedelta(minutes=response_json['delivery_time'])
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
            items = []
            sms_items_info = []
            total_sum = 0
            for item in response_json['items']:
                menu_item = MenuItem.get_by_id(int(item['item_id']))
                for i in xrange(item['quantity']):
                    items.append(menu_item)
                    total_sum += menu_item.price
                sms_items_info.append((menu_item.title, item['quantity']))

            # mastercard
            payment_id = response_json['payment'].get('payment_id')
            mastercard = response_json['payment'].get('mastercard', False)
            apply_discount = mastercard and not client.has_mastercard_orders

            # TODO iOS 1.0.2 bug
            if not mastercard and 'DoubleB/1.0 ' in self.request.headers["User-Agent"]:
                request_total_sum = response_json["total_sum"]
                if not client.has_mastercard_orders and request_total_sum != total_sum:
                    logging.warning("iOS discount bug")
                    apply_discount = True
            # TODO end

            if apply_discount:
                client.has_mastercard_orders = True
                most_expensive_item = max(items, key=lambda i: i.price)
                total_sum -= most_expensive_item.price / 2

            if payment_type_id == CARD_PAYMENT_TYPE and not payment_id:
                binding_id = response_json['payment']['binding_id']
                alpha_client_id = response_json['payment']['client_id']
                return_url = response_json['payment']['return_url']

                payment_id = alfa_bank.hold_and_check(order_id, total_sum, return_url, alpha_client_id, binding_id)
                if not payment_id:
                    memcache.delete(cache_key)
                    self.abort(400)

            if payment_type_id == BONUS_PAYMENT_TYPE:
                cup_count = len(items)
                activation = empatika_promos.activate_promo(client_id, config.FREE_COFFEE_PROMO_ID, cup_count)
                payment_id = str(activation['activation']['id'])

            client.put()
            order = Order(id=order_id, client_id=client_id, venue_id=venue_id, total_sum=total_sum,
                          coordinates=coordinates, comment=comment, status=NEW_ORDER, device_type=device_type,
                          delivery_time=delivery_time, payment_type_id=payment_type_id, payment_id=payment_id,
                          mastercard=mastercard, items=[item.key for item in items])
            order.put()
            memcache.delete(cache_key)

            local_delivery_time = delivery_time + config.TIMEZONE_OFFSET
            sms_text = u"Заказ №%s (%s) Сумма: %s Готовность к: %s %s Тип оплаты: %s" % (
                order_id, client_name, total_sum, local_delivery_time,
                ', '.join("%s X %s" % i for i in sms_items_info),
                [u"Наличные", u"Карта", u"Бонусы"][payment_type_id]
            )
            sms.send_sms('DoubleB', venue.phone_numbers, sms_text)

            self.response.status_int = 201
            self.render_json({'order_id': order_id})
        else:
            memcache.delete(cache_key)
            self.abort(400)


class RegisterOrderHandler(ApiHandler):

    def get(self):
        self.render_json({'order_id': Order.generate_id()})


class StatusHandler(ApiHandler):

    def post(self):
        #TODO errors handling
        response_json = json.loads(self.request.get('orders'))
        orders = []
        for order_id in response_json['orders']:
            order = Order.get_by_id(int(order_id))
            if order:
                orders.append(order)
        self.render_json({'status': [order.status_dict() for order in orders]})


class ReturnOrderHandler(ApiHandler):

    def post(self):
        #TODO errors handling
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
            if order.delivery_time - now > timedelta(minutes=10):
                # return money
                if order.payment_type_id == CARD_PAYMENT_TYPE:
                    return_result = alfa_bank.get_back_blocked_sum(order.payment_id)
                    if str(return_result.get('errorCode', 0)) != '0':
                        logging.error("payment return failed")
                        self.abort(400)
                elif order.payment_type_id == BONUS_PAYMENT_TYPE:
                    try:
                        empatika_promos.cancel_activation(order.payment_id)
                    except empatika_promos.EmpatikaPromosError as e:
                        logging.exception(e)
                        self.abort(400)

                order.status = CANCELED_BY_CLIENT_ORDER
                order.return_datetime = datetime.utcnow()
                order.put()

                # send sms
                venue = Venue.get_by_id(order.venue_id)
                client = Client.get_by_id(order.client_id)
                sms_text = u"[Отмена] Заказ №%s (%s) Сумма: %s Тип оплаты: %s" % (
                    order_id, client.name, order.total_sum,
                    [u"Наличные", u"Карта", u"Бонусы"][order.payment_type_id]
                )
                sms.send_sms("DoubleB", venue.phone_numbers, sms_text)

                # send push
                push_text = u"%s, заказ №%s отменен." % (client.name, order_id)
                if order.payment_type_id == CARD_PAYMENT_TYPE:
                    push_text += u" Ваш платеж будет возвращен на карту в течение нескольких минут."
                push.send_order_push(order_id, order.status, push_text, order.device_type)

                self.render_json({
                    'error': 0,
                    'order_id': order.key.id()
                })
                logging.info(u'заказ %d отменен' % order_id)
            else:
                self.response.status_int = 412
                self.render_json({
                    'error': 1,
                    'description': u'Отмена заказа невозможна, так как до его исполнения осталось менее 10 минут.'
                })


class CheckOrderHandler(ApiHandler):
    def post(self):
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
