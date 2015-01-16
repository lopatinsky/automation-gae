# coding=utf-8
import time

from .base import ApiHandler
from methods import alfa_bank, empatika_wallet


class DepositToWalletHandler(ApiHandler):
    def post(self):
        client_id = self.request.get("client_id")
        binding_id = self.request.get("binding_id")
        amount = self.request.get_range("amount")

        order_number = "dp_%s_%s" % (client_id, int(time.time()))
        alfa_order_id = alfa_bank.hold_and_check(order_number, amount * 100, "http://", client_id, binding_id)
        if not alfa_order_id:
            self.response.set_status(400)
            self.render_json({
                "description": u"Ошибка перевода с карты"
            })

        wallet_source = "alfa:%s" % alfa_order_id
        try:
            wallet_result = empatika_wallet.deposit(client_id, amount * 100, wallet_source)
        except empatika_wallet.EmpatikaWalletError as e:
            alfa_bank.get_back_blocked_sum(alfa_order_id)

            self.response.set_status(400)
            self.render_json({
                "description": e.message
            })
        else:
            alfa_bank.pay_by_card(alfa_order_id, 0)
            self.render_json({
                "balance": wallet_result["balance"] / 100
            })
