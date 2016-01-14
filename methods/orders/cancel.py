# coding=utf-8
import logging
from datetime import datetime

from google.appengine.ext import deferred

from models.config.config import config, EMAIL_FROM, AUTO_APP
from methods import empatika_wallet, push, paypal
from methods.emails import admins, postmark
from methods import alfa_bank, empatika_promos
from methods.empatika_wallet import get_balance
from methods.sms import sms_pilot
from models import Client, Venue
from models.order import CANCELED_BY_BARISTA_ORDER, CANCELED_BY_CLIENT_ORDER
from models.share import SharedPromo

__author__ = 'dvpermyakov'


def cancel_order(order, status, namespace, comment=None):
    success = True
    if order.has_card_payment:
        legal = Venue.get(order.venue_id).legal.get()
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
        if order.wallet_payment > 0 and config.APP_KIND == AUTO_APP:
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
        if order.subscription_details:
            subscription = order.subscription_details.subscription.get()
            subscription.recover(order.subscription_details.amount)
        if order.geo_push:
            geo_push = order.geo_push.get()
            geo_push.recover()
        if order.left_basket_promo:
            left_basket_promo = order.left_basket_promo.get()
            left_basket_promo.recover()

        order.status = status
        order.return_datetime = datetime.utcnow()
        order.return_comment = comment
        order.email_key_done = None
        order.email_key_cancel = None
        order.email_key_postpone = None
        order.email_key_confirm = None
        order.put()

        if order.shared_promo:
            shared_promo = order.shared_promo.get()
            
            if order.client_id == shared_promo.recipient.id():
                shared_promo.recipient_promo_success = False
                
            elif order.client_id == shared_promo.sender.id():
                shared_promo.sender_promo_success = False

            shared_promo.put()

        if status == CANCELED_BY_BARISTA_ORDER:
            client = Client.get(order.client_id)
            push_text = u"%s, заказ №%s отменен." % (client.name, order.number)
            if order.has_card_payment:
                push_text += u" Ваш платеж будет возвращен на карту в течение нескольких минут.\n"
            if success_wallet_payment_reverse:
                push_text += u" Бонусные баллы были возвращены на Ваш счет.\n"
            if comment:
                push_text += " " + comment
            push.send_order_push(order, push_text, namespace)
        elif status == CANCELED_BY_CLIENT_ORDER:
            message = u"Заказ из мобильного приложения №%s отменен клиентом" % order.key.id()
            venue = Venue.get(order.venue_id)
            try:
                sms_pilot.send_sms(venue.phones, message)
            except:
                pass
            for email in venue.emails:
                if email:
                    deferred.defer(postmark.send_email, EMAIL_FROM, email, message, "<html></html>")
    return success
