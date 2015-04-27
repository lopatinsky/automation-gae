# coding=utf-8
import logging
import datetime
from google.appengine.ext import ndb
from handlers.api.base import ApiHandler
from methods import alfa_bank, email, empatika_promos
from models import Order, Venue, NEW_ORDER, READY_ORDER, CARD_PAYMENT_TYPE, Client, SharedFreeCup


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
            if order.payment_type_id == CARD_PAYMENT_TYPE:
                alfa_bank.deposit(order.payment_id, 0)  # TODO check success
            order.status = READY_ORDER
            order.activate_cash_back()
            client_key = ndb.Key(Client, order.client_id)
            free_cup = SharedFreeCup.query(SharedFreeCup.recipient == client_key,
                                           SharedFreeCup.status == SharedFreeCup.READY).get()
            if free_cup:
                free_cup.deactivate_cup()

            order.actual_delivery_time = datetime.datetime.utcnow()
            order.put()
