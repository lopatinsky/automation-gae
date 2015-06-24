# coding=utf-8
from datetime import datetime
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb
from config import config
from methods import alfa_bank, push, paypal
from models import Client
from models.share import SharedPromo
from models.order import READY_ORDER

__author__ = 'dvpermyakov'


def done_order(order, namespace, with_push=True):
    total_cash_back = 0
    if config.WALLET_ENABLED:
        total_cash_back = order.activate_cash_back()
    if config.GIFT_ENABLED:
        order.activate_gift_points()

    order.status = READY_ORDER
    order.email_key_done = None
    order.email_key_cancel = None
    order.email_key_postpone = None
    order.actual_delivery_time = datetime.utcnow()
    order.put()

    client_key = ndb.Key(Client, order.client_id)
    shared_promo = SharedPromo.query(SharedPromo.recipient == client_key, SharedPromo.status == SharedPromo.READY).get()
    if shared_promo:
        shared_promo.deactivate(namespace_manager.get_namespace())

    if order.has_card_payment:
        alfa_bank.deposit(order.payment_id, 0)  # TODO check success
    elif order.has_paypal_payment:
        paypal.capture(order.payment_id, order.total_sum - order.wallet_payment)

    if with_push:
        text = u"Заказ №%s выдан." % order.key.id()
        if total_cash_back:
            text += u" Начислены бонусы на Ваш счет в размере %s" % total_cash_back
        push.send_order_push(order, text, namespace, silent=True)
