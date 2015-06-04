from datetime import datetime
from google.appengine.ext import ndb
from methods import alfa_bank, push, paypal
from models import READY_ORDER, SharedFreeCup, Client

__author__ = 'dvpermyakov'


def done_order(order):
    order.activate_cash_back()
    order.activate_gift_points()

    order.status = READY_ORDER
    order.actual_delivery_time = datetime.utcnow()
    order.put()

    client_key = ndb.Key(Client, order.client_id)
    free_cup = SharedFreeCup.query(SharedFreeCup.recipient == client_key,
                                   SharedFreeCup.status == SharedFreeCup.READY).get()
    if free_cup:
        free_cup.deactivate_cup()

    if order.has_card_payment:
        alfa_bank.deposit(order.payment_id, 0)  # TODO check success
    elif order.has_paypal_payment:
        paypal.capture(order.payment_id, order.total_sum - order.wallet_payment)
    push.send_order_ready_push(order)
