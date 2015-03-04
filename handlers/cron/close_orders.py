# coding=utf-8
import logging
import datetime
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
                if order.mastercard:
                    points = len(order.items)
                    try:
                        empatika_promos.register_order(order.client_id, points, order.key.id())
                    except empatika_promos.EmpatikaPromosError as e:
                        logging.exception(e)
            order.status = READY_ORDER

            client = Client.get_by_id(order.client_id)
            if not client:
                logging.error('Has not client %s' % order.client_id)
            else:
                free_cup = SharedFreeCup.query(SharedFreeCup.recipient == client.key).get()
                if free_cup.status == SharedFreeCup.ACTIVE:
                    free_cup.activate_cup()

            order.actual_delivery_time = datetime.datetime.utcnow()
            order.put()
