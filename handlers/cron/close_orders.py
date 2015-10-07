# coding=utf-8
import logging
from datetime import datetime, timedelta

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata

from handlers.api.base import ApiHandler
from methods.emails import admins
from models import Order, Venue
from models.order import NOT_CANCELED_STATUSES, READY_ORDER
from methods.orders.done import done_order

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
            namespace_manager.set_namespace(namespace)
            for order in namespace_orders[namespace]:
                venue = Venue.get_by_id(order.venue_id)
                venue_title = venue.title if venue else u'Не определено'
                mail_body += u'%s (%s),\n' % (order.key.id(), venue_title)
        if namespace_orders:
            namespace_manager.set_namespace('')
            admins.send_error("order", "Orders not closed", mail_body)