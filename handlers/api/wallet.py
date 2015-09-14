# coding=utf-8
import logging
import time

from .base import ApiHandler
from models.config.config import config
from methods import alfa_bank, empatika_wallet
from models.legal import LegalInfo


class DepositToWalletHandler(ApiHandler):
    def post(self):
        client_id = self.request.get("client_id") or int(self.request.headers.get('Client-Id', 0))
        binding_id = self.request.get("binding_id")
        amount = self.request.get_range("amount")

        legal = LegalInfo.query().get()  # TODO find solution for multiple legals

        order_number = "dp_%s_%s" % (client_id, int(time.time()))
        success, result = alfa_bank.create_simple(legal.alfa_login, legal.alfa_password, amount, order_number, "_",
                                                  client_id)
        if not success:
            self.response.set_status(400)
            self.render_json({
                "description": u"Ошибка перевода с карты"
            })
            return

        alfa_order_id = result
        success, error = alfa_bank.hold_and_check(legal.alfa_login, legal.alfa_password, alfa_order_id, binding_id)
        if not success:
            self.response.set_status(400)
            self.render_json({
                "description": u"Ошибка перевода с карты"
            })
            return

        wallet_source = "alfa:%s" % alfa_order_id
        try:
            wallet_result = empatika_wallet.deposit(client_id, amount * 100, wallet_source)
        except empatika_wallet.EmpatikaWalletError as e:
            alfa_bank.reverse(legal.alfa_login, legal.alfa_password, alfa_order_id)

            self.response.set_status(400)
            self.render_json({
                "description": e.message
            })
        else:
            alfa_bank.deposit(legal.alfa_login, legal.alfa_password, alfa_order_id, 0)
            self.render_json({
                "balance": wallet_result["balance"] / 100.0
            })


class WalletBalanceHandler(ApiHandler):
    def get(self):
        client_id = self.request.get("client_id") or self.request.headers.get('Client-Id')
        if not client_id:
            self.abort(400)
        client_id = int(client_id)
        if config.WALLET_API_KEY:
            wallet_balance = empatika_wallet.get_balance(client_id)
            if wallet_balance is None:
                logging.info(u'Не удалось получить баланс пользователя')
                self.abort(503)  # todo: think about new logic
        else:
            wallet_balance = 0
        self.render_json({
            "balance": wallet_balance / 100.0,
        })
