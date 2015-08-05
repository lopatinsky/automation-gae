from .base import ApiHandler
from methods.orders.validation.precheck import set_client_info


class ClientHandler(ApiHandler):
    def post(self):
        client_json = {
            'id': self.request.get_range('client_id'),
            'name': self.request.get('client_name'),
            'phone': self.request.get('client_phone'),
            'email': self.request.get('client_email')
        }
        set_client_info(client_json)
        self.render_json({})
