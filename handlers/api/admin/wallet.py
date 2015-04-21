# coding=utf-8
import time
from methods import empatika_wallet

from methods.auth import write_access_required
from .base import AdminApiHandler
from methods.empatika_wallet import EmpatikaWalletError
from models import Client


class WalletDepositHandler(AdminApiHandler):
    @write_access_required
    def post(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.response.set_status(400)
            self.render_json({"description": u'Клиент не найден'})
            return
        amount = self.request.get_range('amount', default=None)
        if amount is None or amount < 1:
            self.response.set_status(400)
            self.render_json({"description": u'Неверная сумма'})
            return

        wallet_source = "barista:%s:%s" % (self.user.login, int(time.time()))
        try:
            wallet_result = empatika_wallet.deposit(client_id, amount * 100, wallet_source)
        except EmpatikaWalletError as e:
            self.response.set_status(400)
            self.render_json({
                "description": e.message
            })
        else:
            self.render_json({
                "balance": wallet_result["balance"] / 100.0
            })
