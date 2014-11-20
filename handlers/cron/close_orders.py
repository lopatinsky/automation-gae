# coding=utf-8
import logging
from google.appengine.api import app_identity, mail
from handlers.api.base import ApiHandler
from methods import alfa_bank, empatika_promos
from models import Order, NEW_ORDER, READY_ORDER, CARD_PAYMENT_TYPE


_EMAIL_SENDER = "order_errors@%s.appspotmail.com" % app_identity.get_application_id()


class CloseOpenedOrdersHandler(ApiHandler):
    def get(self):
        orders = Order.query(Order.status == NEW_ORDER).fetch()
        if not orders:
            return

        mail_body = u"List of orders not closed:\n" + "\n".join(order.key.id() for order in orders)
        mail.send_mail_to_admins(_EMAIL_SENDER, "[DoubleB] Orders not closed", mail_body)

        for order in orders:
            logging.info("closing order %s", order.key.id())
            if order.payment_type_id == CARD_PAYMENT_TYPE:
                alfa_bank.pay_by_card(order.payment_id, 0)  # TODO check success
                if order.mastercard:
                    points = len(order.items)
                    try:
                        empatika_promos.register_order(order.client_id, points, order.key.id())
                    except empatika_promos.EmpatikaPromosError as e:
                        logging.exception(e)
            order.status = READY_ORDER
            order.put()
