# coding=utf-8
from google.appengine.api.namespace_manager import namespace_manager
from webapp2 import RequestHandler
from models import Order
from models.order import CANCELED_BY_BARISTA_ORDER
from methods.orders.done import done_order
from methods.orders.cancel import cancel_order

__author__ = 'dvpermyakov'


class DoneOrderHandler(RequestHandler):
    def get(self):
        email_key = self.request.get('key')
        if not email_key:
            self.abort(403)
        order = Order.query(Order.email_key_done == email_key).get()
        if not order:
            return self.response.write(u'Невозможно выдать заказ. Возможно, он отменен.')
        done_order(order, namespace_manager.get_namespace)
        self.response.write(u'Заказ успешно выдан!')


class CancelOrderHandler(RequestHandler):
    def get(self):
        email_key = self.request.get('key')
        if not email_key:
            self.abort(403)
        order = Order.query(Order.email_key_cancel == email_key).get()
        if not order:
            return self.response.write(u'Невозможно отменить заказ. Возможно, он выдан.')
        cancel_order(order, CANCELED_BY_BARISTA_ORDER, namespace_manager.get_namespace())
        self.response.write(u'Заказ успешно отменен!')