# coding=utf-8
import datetime
from handlers.api.admin.base import AdminApiHandler
from methods import push, alfa_bank
from models import Order, CARD_PAYMENT_TYPE, CANCELED_BY_BARISTA_ORDER, Client, READY_ORDER

__author__ = 'ilyazorin'


class CancelOrderHandler(AdminApiHandler):
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

            self.render_json({})
        else:
            self.response.status_int = 400
            self.render_json({})


class DoneOrderHandler(AdminApiHandler):
    def post(self):
        order_id = self.request.get_range("order_id")
        order = Order.get_by_id(order_id)
        order.status = READY_ORDER
        order.put()

        if order.payment_type_id == CARD_PAYMENT_TYPE:
            alfa_bank.pay_by_card(order.payment_id, 0)
        push.send_order_push(order_id, order.status, "", order.device_type, silent=True)

        self.render_json({})


class PostponeOrderHandler(AdminApiHandler):
    def post(self):
        order_id = self.request.get_range("order_id")
        mins = self.request.get_range("mins")

        order = Order.get_by_id(order_id)
        order.delivery_time += datetime.timedelta(mins)
        order.put()

        time_str = order.delivery_time.strftime("%H:%M")
        client = Client.get_by_id(order.client_id)
        push_text = u"%s, готовность заказа №%s была изменена на %s" % (client.name, order_id, time_str)
        push.send_order_push(order_id, order.status, push_text, order.device_type, new_time=order.delivery_time)

        self.render_json({})
