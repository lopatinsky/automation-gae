from methods import paypal
from .base import ApiHandler
from models import Client


class BindPaypalHandler(ApiHandler):
    def post(self):
        client_id = self.request.get_range("client_id")
        client = Client.get_by_id(client_id)
        auth_code = self.request.get("auth_code")

        client.paypal_refresh_token = paypal.get_refresh_token(auth_code)
        client.put()
        self.render_json({})


class UnbindPaypalHandler(ApiHandler):
    def post(self):
        client_id = self.request.get_range("client_id")
        client = Client.get_by_id(client_id)
        client.paypal_refresh_token = None
        client.put()
        self.render_json({})
