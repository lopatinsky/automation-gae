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
        statuses = list(NOT_CANCELED_STATUSES)
        statuses.remove(READY_ORDER)
        namespace_orders = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            orders = Order.query(Order.status.IN(statuses),
                                 Order.delivery_time < datetime.utcnow() - timedelta(hours=HOURS_BEFORE)).fetch()
            if orders:
                logging.info('-----------------------------')
                namespace_orders[namespace] = orders
            for order in orders:
                logging.info("closing order id=%s, namespace=%s" % (order.key.id(), namespace))
                done_order(order, namespace, with_push=False)
        mail_body = u"List of orders not closed:\n"
        for namespace in namespace_orders.keys():
            mail_body += u'In namespace = %s:\n' % namespace
            for order in namespace_orders[namespace]:
                venue = Venue.get_by_id(order.venue_id)
                venue_title = venue.title if venue else u'Не определено'
                mail_body += u'%s (%s),\n\n' % (order.key.id(), venue_title)
        if namespace_orders:
            email.send_error("order", "Orders not closed", mail_body)