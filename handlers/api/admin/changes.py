# coding=utf-8
import datetime
import logging
from config import config
from handlers.api.admin.base import AdminApiHandler
from methods import push, alfa_bank, empatika_promos
from models import Order, CARD_PAYMENT_TYPE, CANCELED_BY_BARISTA_ORDER, Client, READY_ORDER, BONUS_PAYMENT_TYPE

__author__ = 'ilyazorin'


class CancelOrderHandler(AdminApiHandler):
    def post(self, order_id):
        comment = self.request.get('comment')
        order = Order.get_by_id(order_id)

        success = True
        if order.payment_type_id == CARD_PAYMENT_TYPE:
            return_result = alfa_bank.get_back_blocked_sum(order.payment_id)
            success = str(return_result['errorCode']) == '0'
        elif order.payment_type_id == BONUS_PAYMENT_TYPE:
            try:
                empatika_promos.cancel_activation(order.payment_id)
            except empatika_promos.EmpatikaPromosError as e:
                logging.exception(e)
                success = False

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
    def post(self, order_id):
        order = Order.get_by_id(order_id)
        order.status = READY_ORDER
        order.put()

        if order.payment_type_id == CARD_PAYMENT_TYPE:
            alfa_bank.pay_by_card(order.payment_id, 0)  # TODO check success
            if order.mastercard:
                points = len(order.items)
                try:
                    empatika_promos.register_order(order.client_id, points)
                except empatika_promos.EmpatikaPromosError as e:
                    logging.exception(e)
        push.send_order_push(order_id, order.status, u"Заказ №%s выдан." % str(order.key.id()),
                             order.device_type, silent=True)

        self.render_json({})


class PostponeOrderHandler(AdminApiHandler):
    def post(self, order_id):
        mins = self.request.get_range("mins")

        order = Order.get_by_id(order_id)
        order.delivery_time += datetime.timedelta(mins)
        order.put()

        local_delivery_time = order.delivery_time + config.TIMEZONE_OFFSET
        time_str = local_delivery_time.strftime("%H:%M")
        client = Client.get_by_id(order.client_id)
        push_text = u"%s, готовность заказа №%s была изменена на %s" % (client.name, order_id, time_str)
        push.send_order_push(order_id, order.status, push_text, order.device_type, new_time=order.delivery_time)

        self.render_json({})
