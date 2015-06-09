# coding=utf-8
__author__ = 'dvpermyakov'

from webapp2 import RequestHandler
from models import Order, Client
from methods import email, sms_pilot
import logging


class CheckOrderSuccessHandler(RequestHandler):
    def post(self):
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        if not order.response_success:
            client = Client.get_by_id(order.client_id)
            body = u"Order timeout in app (bad internet connection)\n" \
                   u"Order number: %s\n" \
                   u"Client name: %s %s\n" \
                   u"Client phone: %s" % (order_id, client.name, client.surname, client.tel)
            logging.warning(body)
            email.send_error('network', 'Order timeout', body)

            sms_text = u"%s, Ваш заказ №%s принят. Проверьте историю заказов." % (client.name, order_id)
            phone = client.tel
            if len(phone) == 11 and phone[0] == "8":
                phone = "7" + phone[1:]
            sms_pilot.send_sms("DoubleB", [phone], sms_text)