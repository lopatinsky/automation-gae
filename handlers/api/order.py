# coding:utf-8
from google.appengine.ext.ndb import GeoPt
from handlers.api.base import ApiHandler
import json
import re
from datetime import datetime, timedelta
from methods import sms
from models import Client, MenuItem, CARD_PAYMENT_TYPE, Order, NEW_ORDER, Venue, CANCELED_BY_CLIENT_ORDER

__author__ = 'ilyazorin'


class OrderHandler(ApiHandler):

    def post(self):
        #TODO errors handling
        response_json = json.loads(self.request.get('order'))
        order_id = response_json['order_id']
        venue_id = response_json['venue_id']
        total_sum = response_json['total_sum']
        coordinates = GeoPt(response_json['coordinates'])
        comment = response_json['comment']
        device_type = response_json['device_type']
        delivery_time = datetime.utcnow() + timedelta(minutes=response_json['delivery_time'])
        client_id = response_json['client']['client_id']

        client = Client.get_by_id(client_id)
        client_name = response_json['client']['name']
        client_tel = re.sub("[^0-9]", "", response_json['client']['tel'])
        if client.name != client_name or client.tel != client_tel:
            client.name = client_name
            client.tel = client_tel
            client.put()

        payment_type_id = response_json['payment']['type_id']
        payment_id = response_json['payment']['payment_id']

        items = []
        sms_items_info = []
        for item in response_json['items']:
            menu_item = MenuItem.get_by_id(item['item_id'])
            for i in xrange(item['quantity']):
                items.append(menu_item)
            sms_items_info.append((menu_item.title, item['quantity']))

        #TODO card payment
        if payment_type_id == CARD_PAYMENT_TYPE:
            pass

        order = Order(id=order_id, client_id=client_id, venue_id=venue_id, total_sum=total_sum, coordinates=coordinates,
                      comment=comment, status=NEW_ORDER, device_type=device_type, delivery_time=delivery_time,
                      payment_type_id=payment_type_id, payment_id=payment_id,
                      items=[item.key for item in items])
        order.put()

        venue = Venue.get_by_id(venue_id)
        sms_text = u"Заказ №%s (%s) Сумма: %s Готовность к: %s %s Тип оплаты: %s" % (
            order_id, client_name, total_sum, delivery_time,
            ', '.join("%s X %s" % i for i in sms_items_info),
            [u"Наличные", u"Карта"][payment_type_id]
        )
        sms.send_sms('DoubleB', venue.phone_numbers, sms_text)

        self.response.status_int = 201
        self.render_json({'order_id': order_id})


class RegisterOrderHandler(ApiHandler):

    def get(self):
        self.render_json({'order_id': Order.generate_id()})


class StatusHandler(ApiHandler):

    def post(self):
        #TODO errors handling
        response_json = json.loads(self.request.get('orders'))
        orders = []
        for order_id in response_json:
            order = Order.get_by_id(order_id)
            if order:
                orders.append(order)
        self.render_json({'status': order.status_dict() for order in orders})


class ReturnOrderHandler(ApiHandler):

    def post(self):
        #TODO errors handling
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if order:
            now = datetime.utcnow()
            if now - order.delivery_time > timedelta(minutes=10):
                order.status = CANCELED_BY_CLIENT_ORDER
                order.put()
                self.render_json({
                    'error': 0,
                    'order_id': order.key.id()
                })
            else:
                self.render_json({
                    'error': 1,
                    'description': u'Отмена заказа невозможна, так как до его исполнения осталось менее 10 минут.'
                })
        else:
            self.abort(400)
