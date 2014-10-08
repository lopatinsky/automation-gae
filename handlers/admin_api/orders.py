# coding=utf-8

from collections import Counter
import datetime
from handlers.api.base import ApiHandler
from methods import push, alfa_bank
from models import Order, Client, NEW_ORDER, CANCELED_BY_CLIENT_ORDER, READY_ORDER, CARD_PAYMENT_TYPE, \
    CANCELED_BY_BARISTA_ORDER


class CheckTimeHandler(ApiHandler):
    def post(self):
        mins = self.request.get_range("mins")
        order_id = self.request.get_range("order_id")

        order = Order.get_by_id(order_id)
        order.delivery_time += datetime.timedelta(mins)
        order.put()

        time_str = order.delivery_time.strftime("%M:%S")
        client = Client.get_by_id(order.client_id)
        push_text = u"%s, готовность заказа №%s была изменена на %s" % (client.name, order_id, time_str)
        push.send_order_push(order_id, order.status, push_text, order.device_type, new_time=order.delivery_time)

        response = {
            'error': 0,
            'info': {
                'time': time_str,
                'order_id': order_id
            }
        }
        self.render_json(response)


class CheckUpdateHandler(ApiHandler):
    def post(self):
        last_date_str = self.request.get("last_order_datetime")
        last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d %H:%M:%S")
        orders = Order.query().filter(Order.date_created > last_date).fetch()
        response = {}
        if orders:
            response['status'] = 1
            for order in orders:
                if order.status != NEW_ORDER:
                    continue
                client = Client.get_by_id(order.client_id)
                client_name, client_surname = client.name.split(None, 1)
                order_data = {
                    'date_created': order.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                    'comment': order.comment,
                    'payment_type_id': order.payment_type_id,
                    'order_id': order.key.id(),
                    'pan': order.pan,
                    'name': client_name,
                    'surname': client_surname,
                    'tel': client.tel,
                    'items': []
                }
                item_keys = Counter(order.items).items()
                for key, count in item_keys:
                    item = key.get()
                    order_data['items'].append({
                        'title': item.title,
                        'price': item.price,
                        'quantity': count
                    })
        else:
            response['status'] = 0
        cancel_keys = Order.query().filter(Order.status == CANCELED_BY_CLIENT_ORDER).fetch(keys_only=True)
        cancel_ids = [k.id() for k in cancel_keys]
        response['cancel'] = cancel_ids
        self.render_json(response)


class OrderDoneHandler(ApiHandler):
    def post(self):
        order_id = self.request.get_range("order_id")
        order = Order.get_by_id(order_id)
        order.status = READY_ORDER
        order.put()

        if order.payment_type_id == CARD_PAYMENT_TYPE:
            alfa_bank.pay_by_card(order.payment_id, 0)
        push.send_order_push(order_id, order.status, "", order.device_type, silent=True)

        response = {
            'status': 1,
            'error': 0,
            'order_id': order_id
        }
        self.render_json(response)


class OrderCancelHandler(ApiHandler):
    def post(self):
        order_id = self.request.get_range('order_id')
        comment = self.request.get('comment')
        order = Order.get_by_id(order_id)

        success = True
        if order.payment_type_id == CARD_PAYMENT_TYPE:
            return_result = alfa_bank.get_back_blocked_sum(order.payment_id)
            success = str(return_result['errorCode']) == '0'

        if success:
            order.status = CANCELED_BY_BARISTA_ORDER
            order.return_datetime = datetime.datetime.utcnow()
            order.return_comment = comment
            order.put()

            client = Client.get_by_id(order.client_id)
            push_text = u"%s, заказ №%s отменен." % (client.name, order_id)
            if order.payment_type_id == CARD_PAYMENT_TYPE:
                push_text += u" Ваш платеж будет возвращен на карту в течение нескольких минут."
            push.send_order_push(order_id, order.status, push_text, order.device_type)

            response = {
                'error': 0,
                'order_id': order_id
            }
        else:
            response = {
                'error': 1,
                'error_descr': 'Alfabank error'
            }
        self.render_json(response)


class OrderStatusUpdateHandler(ApiHandler):
    def post(self):
        order_id = self.request.get_range("order_id")
        status = self.request.get_range("status")
        order = Order.get_by_id(order_id)
        order.status = status
        order.put()
        self.render_json({
            'error': 0,
            'order_id': order_id,
            'status': status
        })
