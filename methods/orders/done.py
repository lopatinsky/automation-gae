# coding=utf-8
from datetime import datetime, timedelta

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.api.taskqueue import taskqueue
from google.appengine.ext import ndb

from models.config.config import config
from methods import alfa_bank, push, paypal
from models import Client
from models.share import SharedPromo
from models.order import READY_ORDER
from models.specials import ReviewPush
from models.venue import Venue

__author__ = 'dvpermyakov'


def send_review_push(order):
    namespace_manager.set_namespace(order.key.namespace())
    module = config.REVIEW_MODULE
    if module and module.status:
        review = ReviewPush(order=order.key)
        review.put()
        start = datetime.utcnow() + timedelta(seconds=module.wait_seconds)
        taskqueue.add(url='/task/pushes/review', method='POST', eta=start, params={
            'review_id': review.key.id()
        })


def done_order(order, namespace, with_push=True):
    total_cash_back = 0
    point_sum = 0
    if config.WALLET_ENABLED:
        total_cash_back = order.activate_cash_back()
    if config.GIFT_ENABLED:
        point_sum = order.activate_gift_points()

    for share_gift in order.shared_gift_details:
        share_gift.gift.get().deactivate()

    for performing in order.promo_code_performings:
        performing = performing.get()
        promo_code = performing.promo_code.get()
        if not promo_code.persist:
            performing.close()

    order.status = READY_ORDER
    order.email_key_done = None
    order.email_key_cancel = None
    order.email_key_postpone = None
    order.email_key_confirm = None
    order.actual_delivery_time = datetime.utcnow()

    client_key = ndb.Key(Client, order.client_id)
    shared_promo = SharedPromo.query(SharedPromo.recipient == client_key, SharedPromo.status == SharedPromo.READY).get()
    if shared_promo:
        shared_promo.deactivate(namespace_manager.get_namespace())

    if order.has_card_payment:
        legal = Venue.get(order.venue_id).legal.get()
        alfa_bank.deposit(legal.alfa_login, legal.alfa_password, order.payment_id, 0)  # TODO check success
    elif order.has_paypal_payment:
        paypal.capture(order.payment_id, order.total_sum - order.wallet_payment)

    order.put()

    if with_push:
        text = u"Заказ №%s выдан." % order.number
        if point_sum:
            text += u" Начислены баллы в размере %s." % point_sum
        if total_cash_back:
            text += u" Начислены бонусы на Ваш счет в размере %s." % (total_cash_back / 100.0)
        push.send_order_push(order, text, namespace, silent=True)
        send_review_push(order)
