# coding=utf-8
import logging
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from handlers.api.base import ApiHandler
from methods import email
from models import Order, Venue
from models.order import NOT_CANCELED_STATUSES, READY_ORDER
from methods.orders.done import done_order
from datetime import datetime, timedelta

HOURS_BEFORE = 3


class CloseOpenedOrdersHandler(ApiHandler):
    def get(self):
        namespace_orders = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            statuses = NOT_CANCELED_STATUSES
            statuses.remove(READY_ORDER)
            orders = Order.query(Order.status.IN(statuses),
                                 Order.delivery_time < datetime.utcnow() - timedelta(hours=HOURS_BEFORE)).fetch()
            if orders:
                namespace_orders[namespace] = orders
            for order in orders:
                logging.info("closing order %s", order.key.id())
                done_order(order, namespace)
        mail_body = u"List of orders not closed:\n"
        for namespace in namespace_orders.keys():
            mail_body += u'In namespace = %s:\n' % namespace
            mail_body += u''.join("%s (%s),\n\n" % (str(order.key.id()), Venue.get_by_id(order.venue_id).title)
                                  for order in namespace_orders[namespace])
        email.send_error("order", "Orders not closed", mail_body)