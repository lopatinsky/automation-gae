from methods import paypal
from .base import ApiHandler
from methods.paypalrestsdk import exceptions as paypal_exceptions
from models import Client


class BindPaypalHandler(ApiHandler):
    def post(self):
        client_id = self.request.get_range("client_id") or int(self.request.headers.get('Client-Id', 0))
        client = Client.get_by_id(client_id)
        auth_code = self.request.get("auth_code")

        try:
            client.paypal_refresh_token = paypal.get_refresh_token(auth_code)
        except paypal_exceptions.BadRequest:
            self.abort(400)
        else:
            client.put()
            user_data = paypal.get_user_info(client.paypal_refresh_token)
            self.render_json({'user': user_data})


class UnbindPaypalHandler(ApiHandler):
    def post(self):
        client_id = self.request.get_range("client_id") or int(self.request.headers.get('Client-Id', 0))
        client = Client.get_by_id(client_id)
        client.paypal_refresh_token = None
        client.put()
        self.render_json({})
