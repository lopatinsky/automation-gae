# coding:utf-8
import logging
from google.appengine.ext.ndb import GeoPt
from handlers.api.base import ApiHandler
import json
from time import time as time_time
import re
from datetime import datetime, timedelta
from methods import alfa_bank, sms, push
from models import Client, MenuItem, CARD_PAYMENT_TYPE, Order, NEW_ORDER, Venue, CANCELED_BY_CLIENT_ORDER, IOS_DEVICE, \
    BONUS_PAYMENT_TYPE, PaymentType, STATUS_AVAILABLE

__author__ = 'ilyazorin'


class OrderHandler(ApiHandler):

    def post(self):
        #TODO errors handling
        response_json = json.loads(self.request.get('order'))
        order_id = int(response_json['order_id'])
        venue_id = int(response_json['venue_id'])
        coordinates = GeoPt(response_json.get('coordinates', None))
        comment = response_json['comment']
        device_type = response_json.get('device_type', IOS_DEVICE)
        delivery_time = datetime.utcnow() + timedelta(minutes=response_json['delivery_time'])
        client_id = int(response_json['client']['id'])

        client = Client.get_by_id(int(client_id))
        name = response_json['client']['name'].split(None, 1)
        client_name = name[0]
        client_surname = name[1] if len(name) > 1 else ""
        client_tel = re.sub("[^0-9]", "", response_json['client']['phone'])
        if client.name != client_name or client.surname != client_surname or client.tel != client_tel:
            client.name = client_name
            client.surname = client_surname
            client.tel = client_tel
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

            payment_id = response_json['payment'].get('payment_id')
            if payment_type_id == CARD_PAYMENT_TYPE and not payment_id:
                # mastercard
                if response_json['payment']['mastercard'] and not client.has_mastercard_orders:
                    client.has_mastercard_orders = True
                    client.put()
                    total_sum = (total_sum + 1) / 2

                binding_id = response_json['payment']['binding_id']
                alpha_client_id = response_json['payment']['client_id']
                return_url = response_json['payment']['return_url']
                tie_result = alfa_bank.tie_card(total_sum * 100, int(time_time()), return_url, alpha_client_id,
                                                'MOBILE')
                if 'errorCode' not in tie_result.keys() or str(tie_result['errorCode']) == '0':
                    payment_id = tie_result['orderId']
                    create_result = alfa_bank.create_pay(binding_id, payment_id)
                    if 'errorCode' not in create_result.keys() or str(create_result['errorCode']) == '0':
                        pass
                    else:
                        self.abort(400)
                else:
                    self.abort(400)

            #TODO bonus payment
            if payment_type_id == BONUS_PAYMENT_TYPE:
                pass

            order = Order(id=order_id, client_id=client_id, venue_id=venue_id, total_sum=total_sum,
                          coordinates=coordinates, comment=comment, status=NEW_ORDER, device_type=device_type,
                          delivery_time=delivery_time, payment_type_id=payment_type_id, payment_id=payment_id,
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
        else:
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
            logging.info(u'заказ уже %d выдан или отменен' % order_id)
        else:
            now = datetime.utcnow()
            if order.delivery_time - now > timedelta(minutes=10):
                # return money
                if order.payment_type_id == CARD_PAYMENT_TYPE:
                    return_result = alfa_bank.get_back_blocked_sum(order.payment_id)
                    if str(return_result.get('errorCode', 0)) != '0':
                        logging.error("payment return failed")
                        self.abort(400)

                order.status = CANCELED_BY_CLIENT_ORDER
                order.return_datetime = datetime.utcnow()
                order.put()

                # send sms
                venue = Venue.get_by_id(order.venue_id)
                client = Client.get_by_id(order.client_id)
                sms_text = u"[Отмена] Заказ №%s (%s) Сумма: %s Тип оплаты: %s" % (
                    order_id, client.name, order.total_sum,
                    [u"Наличные", u"Карта"][order.payment_type_id]
                )
                sms.send_sms("DoubleB", venue.phone_numbers, sms_text)

                # send push
                push_text = u"%s, заказ №%s отменен." % (client.name, order_id)
                if order.payment_type_id == CARD_PAYMENT_TYPE:
                    push_text += u" Ваш платеж будет возвращен на карту в течение несколких минут."
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
                logging.info(u'заказ %d отмена невозможна, так как до его исполнения осталось менее 10 минут.' % order_id)
