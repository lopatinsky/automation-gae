# coding=utf-8

from .base import ApiHandler


class DepositToWalletHandler(ApiHandler):
    def post(self):
        client_id = self.request.get("client_id")
        binding_id = self.request.get("binding_id")
        amount = self.request.get("amount")

        # TODO actually deposit

        self.response.set_status(503)
        self.render_json({
            "description": u"Кошелек отключен"
        })
