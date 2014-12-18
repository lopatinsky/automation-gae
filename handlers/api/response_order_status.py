__author__ = 'dvpermyakov'

import webapp2
from models import Order, Client
from .base import ApiHandler
from methods import email
import logging


class CheckOrderSuccessHandler(webapp2.RequestHandler):
    def post(self):
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        if not order.response_success:
            client = Client.get_by_id(order.client_id)
            body = u"Timeout in app (bad internet connection\n" \
                   u"Order number: %s\n" \
                   u"Client name: %s %s\n" \
                   u"Client phone: %s" % (order_id, client.name, client.surname, client.tel)
            logging.warning(body)
            email.send_error('network', 'Order timeout', body)


class ClientSettingSuccessHandler(ApiHandler):
    def post(self):
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        order.response_success = True
        order.put()
        self.render_json({})