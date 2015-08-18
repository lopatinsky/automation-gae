# coding=utf-8
import logging
from datetime import datetime

from google.appengine.ext.deferred import deferred

from methods import empatika_wallet, push, paypal
from methods.emails import admins
from methods import alfa_bank, empatika_promos
from methods.empatika_wallet import get_balance
from models import Client
from models.venue import Venue

__author__ = 'dvpermyakov'


def cancel_order(order, status, namespace, comment=None, with_push=True):
    success = True
    if order.has_card_payment:
        legal = Venue.get_by_id(order.venue_id).legal.get()
        return_result = alfa_bank.reverse(legal.alfa_login, legal.alfa_password, order.payment_id)
        success = str(return_result['errorCode']) == '0'
    elif order.has_paypal_payment:
        success, error = paypal.void(order.payment_id)
    if success:
        for gift_detail in order.gift_details:
            try:
                empatika_promos.cancel_activation(gift_detail.activation_id)
            except empatika_promos.EmpatikaPromosError as e:
                logging.exception(e)
                admins.send_error("payment", "Cancel activation", str(e))
                success = False
    if success:
        success_wallet_payment_reverse = False
        if order.wallet_payment > 0:
            try:
                empatika_wallet.reverse(order.client_id, order.key.id())
                deferred.defer(get_balance, order.client_id, raise_error=True)  # just to update memcache
                success_wallet_payment_reverse = True
            except empatika_wallet.EmpatikaWalletError as e:
                logging.exception(e)
                admins.send_error("payment", "Wallet reversal failed", str(e))
                # main payment reversed -- do not abort
        for share_gift in order.shared_gift_details:
            gift = share_gift.gift.get()
            gift.recover()
        for performing in order.promo_code_performings:
            performing = performing.get()
            performing.recover()

        order.status = status
        order.return_datetime = datetime.utcnow()
        order.return_comment = comment
        order.email_key_done = None
        order.email_key_cancel = None
        order.email_key_postpone = None
        order.email_key_confirm = None
        order.put()

        if with_push:
            client = Client.get_by_id(order.client_id)
            push_text = u"%s, заказ №%s отменен." % (client.name, order.key.id())
            if order.has_card_payment:
                push_text += u" Ваш платеж будет возвращен на карту в течение нескольких минут.\n"
            if success_wallet_payment_reverse:
                push_text += u" Бонусные баллы были возвращены на Ваш счет.\n"
            if comment:
                push_text += comment
            push.send_order_push(order, push_text, namespace)
    return success