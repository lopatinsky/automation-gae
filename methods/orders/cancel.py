# coding=utf-8
from methods import email, empatika_wallet, push
import logging
from methods import alfa_bank, empatika_promos
from datetime import datetime
from models import Client

__author__ = 'dvpermyakov'


def cancel_order(order, status, comment=None, with_push=True):
    success = True
    if order.has_card_payment:
        return_result = alfa_bank.reverse(order.payment_id)
        success = str(return_result['errorCode']) == '0'
    if success:
        for gift_detail in order.gift_details:
            try:
                empatika_promos.cancel_activation(gift_detail.activation_id)
            except empatika_promos.EmpatikaPromosError as e:
                logging.exception(e)
                email.send_error("payment", "Cancel activation", str(e))
                success = False
    if success:
        if order.wallet_payment > 0:
            try:
                empatika_wallet.reverse(order.client_id, order.key.id())
            except empatika_wallet.EmpatikaWalletError as e:
                logging.exception(e)
                email.send_error("payment", "Wallet reversal failed", str(e))
                # main payment reversed -- do not abort

        order.status = status
        order.return_datetime = datetime.utcnow()
        order.return_comment = comment
        order.put()

        if with_push:
            client = Client.get_by_id(order.client_id)
            push_text = u"%s, заказ №%s отменен." % (client.name, order.key.id())
            if order.has_card_payment:
                push_text += u" Ваш платеж будет возвращен на карту в течение нескольких минут.\n"
                push_text += comment
            push.send_order_push(order.key.id(), order.status, push_text, order.device_type)
    return success