__author__ = 'dvpermyakov'

import webapp2
from models import Order
from .base import ApiHandler
from methods import email
import logging


class CheckOrderSuccessHandler(webapp2.RequestHandler):
    def post(self):
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        if not order.response_success:
            logging.warning('to email order error')
            body = 'Order with id=%s did not response to client' % order_id
            email.send_error('network', 'Order error', body)


class ClientSettingSuccessHandler(ApiHandler):
    def post(self):
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        order.response_success = True
        order.put()
        self.render_json({})