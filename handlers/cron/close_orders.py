# coding=utf-8
import logging
import datetime
from handlers.api.base import ApiHandler
from methods import alfa_bank, email, empatika_promos
from models import Order, NEW_ORDER, READY_ORDER, CARD_PAYMENT_TYPE


class CloseOpenedOrdersHandler(ApiHandler):
    def get(self):
        orders = Order.query(Order.status == NEW_ORDER).fetch()
        if not orders:
            return

        mail_body = u"List of orders not closed:\n" + "\n".join(str(order.key.id()) for order in orders)
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
            order.actual_delivery_time = datetime.datetime.utcnow()
            order.put()
