# coding=utf-8
import time

from .base import ApiHandler
from config import config
from methods import alfa_bank, empatika_wallet


class DepositToWalletHandler(ApiHandler):
    def post(self):
        client_id = self.request.get("client_id")
        binding_id = self.request.get("binding_id")
        amount = self.request.get_range("amount")

        order_number = "dp_%s_%s" % (client_id, int(time.time()))
        success, result = alfa_bank.create_simple(amount, order_number, "_", client_id)
        if not success:
            self.response.set_status(400)
            self.render_json({
                "description": u"Ошибка перевода с карты"
            })
            return

        alfa_order_id = result
        success, error = alfa_bank.hold_and_check(alfa_order_id, binding_id)
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
            alfa_bank.reverse(alfa_order_id)

            self.response.set_status(400)
            self.render_json({
                "description": e.message
            })
        else:
            alfa_bank.deposit(alfa_order_id, 0)
            self.render_json({
                "balance": wallet_result["balance"] / 100.0
            })


class WalletBalanceHandler(ApiHandler):
    def get(self):
        client_id = self.request.get("client_id")
        if not client_id:
            self.abort(400)
        client_id = int(client_id)
        if config.WALLET_API_KEY:
            wallet_balance = empatika_wallet.get_balance(client_id)
        else:
            wallet_balance = 0
        self.render_json({
            "balance": wallet_balance / 100.0,
        })
