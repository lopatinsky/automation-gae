from google.appengine.ext import ndb
from handlers.api.base import ApiHandler
from models import Order, NEW_ORDER, READY_ORDER

__author__ = 'ilyazorin'


class CloseOpenedOrdersHandler(ApiHandler):
    orders = Order.query(Order.status == NEW_ORDER).fetch()
    for order in orders:
        order.status = READY_ORDER
    ndb.put_multi(orders)