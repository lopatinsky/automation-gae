# coding=utf-8
import logging
from webapp2 import RequestHandler
from models import Order, Client
from methods.sms import sms_pilot
from methods.emails import admins
from google.appengine.api.namespace_manager import namespace_manager
from methods.rendering import sms_phone

__author__ = 'dvpermyakov'


class CheckOrderSuccessHandler(RequestHandler):
    def post(self):
        namespace = self.request.get('namespace')
        namespace_manager.set_namespace(namespace)
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        if not order.response_success:
            client = Client.get(order.client_id)
            sms_text = u"%s, Ваш заказ №%s принят. Проверьте историю заказов." % (client.name, order_id)
            sms_pilot.send_sms([sms_phone(client.tel)], sms_text)
