import json

from models import Client
from .base import ApiHandler
from methods.orders.validation.precheck import set_client_info


class ClientHandler(ApiHandler):
    def post(self):
        extra_fields = json.loads(self.request.get('groups', '{}'))
        client_json = {
            'id': self.request.get_range('client_id'),
            'name': self.request.get('client_name'),
            'phone': self.request.get('client_phone'),
            'email': self.request.get('client_email'),
            'groups': extra_fields,
        }
        set_client_info(client_json, self.request.headers)
        self.render_json({})


class ClientSearchHandler(ApiHandler):
    def get(self):
        client = Client.find_first_by_phone(self.request.get('phone'))
        client_id = None if not client else client.key.id()
        self.render_json({'id': client_id})
