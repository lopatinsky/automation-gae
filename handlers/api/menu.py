import logging
from handlers.api.base import ApiHandler
from models import MenuCategory, Client, STATUS_AVAILABLE

__author__ = 'ilyazorin'


_FUCKUP_CLIENTS_MAP = {
    200053: 200500,
    200055: 200646,
    200056: 200252,
    200059: 200188,
}


class MenuHandler(ApiHandler):

    def get(self):
        client_id = self.request.get_range('client_id')
        device_phone = "".join(c for c in self.request.get('device_phone') if '0' <= c <= '9')
        categories = MenuCategory.query().fetch()
        result_dict = {}
        for category in categories:
            result_dict.update(category.dict())
        response = {'menu': result_dict}

        # fuckup iOS 1.1
        if client_id in _FUCKUP_CLIENTS_MAP:
            logging.warning("fuckup found: %s", client_id)
            client_id = _FUCKUP_CLIENTS_MAP[client_id]
        # fuckup end

        client = None
        try:
            client = Client.get_by_id(client_id)
        except:
            pass
        if not client and device_phone:
            client = Client.query(Client.device_phone == device_phone).get()

        if not client:
            client = Client.create()
            client.user_agent = self.request.headers["User-Agent"]
            client.device_phone = device_phone
            client.put()
            logging.info("issued new client_id: %s", client.key.id())
        elif device_phone and device_phone != client.device_phone:
            client.device_phone = device_phone
            client.put()

        response['client_id'] = client.key.id()
        client_name = client.name or ''
        if client.surname:
            client_name += ' ' + client.surname
        response['client_name'] = client_name
        response['client_email'] = client.email or ''
        self.render_json(response)
