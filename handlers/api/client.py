from .base import ApiHandler
from models import Client


class ClientHandler(ApiHandler):
    def post(self):
        client_id = self.request.get_range('client_id')

        client_name = self.request.get('client_name').split()
        name = client_name[0] if client_name else ''
        surname = client_name[1] if len(client_name) >= 2 else ''

        client_phone = self.request.get('client_phone')
        client_phone = ''.join(c for c in client_phone if '0' <= c <= '9')

        client_email = self.request.get('client_email')
        client_emails = client_email.strip().split(' ') if client_email else []

        if client_id:
            client = Client.get_by_id(client_id)
        else:
            if client_phone:
                client = Client.query(Client.tel == client_phone).get()
            else:
                client = None
            if not client and client_emails:
                client = Client.query(Client.email.IN(client_emails)).get()
            if not client:
                return self.render_json({'error': 2})

        client.name = name
        client.surname = surname
        client.tel = client_phone
        client.email = client_emails[0] if len(client_emails) else None
        client.put()
        self.render_json({
            'id': client.key.id(),
            'name': client.name,
            'surname': client.surname,
            'tel': client.tel
        })
