# coding=utf-8
import logging
from handlers.api.base import ApiHandler
from methods import email
from models import Order, Venue
from methods.orders.done import done_order
from models.order import NEW_ORDER


class CloseOpenedOrdersHandler(ApiHandler):
    def get(self):
        orders = Order.query(Order.status == NEW_ORDER).fetch()
        if not orders:
            return

        mail_body = u"List of orders not closed:\n" + \
                    u''.join("%s (%s),\n" % (str(order.key.id()), Venue.get_by_id(order.venue_id).title) for order in orders)
        email.send_error("order", "Orders not closed", mail_body)

        for order in orders:
            logging.info("closing order %s", order.key.id())
            done_order(order)