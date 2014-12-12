from .base import ApiHandler
from models import Client


class ClientHandler(ApiHandler):
    def post(self):
        client_id = self.request.get_range('client_id')
        if not client_id:
            self.render_json({'error': 2})
            return

        client_name = self.request.get('client_name').split()
        name = client_name[0] if client_name else ''
        surname = client_name[1] if len(client_name) >= 2 else ''

        client_phone = self.request.get('client_phone')
        client_phone = ''.join(c for c in client_phone if '0' <= c <= '9')

        client_email = self.request.get('email')

        client = Client.get_by_id(client_id)
        client.name = name
        client.surname = surname
        client.tel = client_phone
        client.email = client_email
        client.put()
        self.render_json({'client': {
            'name': client.name,
            'surname': client.surname,
            'tel': client.tel
        }})
