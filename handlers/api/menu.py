import logging
from handlers.api.base import ApiHandler
from models import MenuCategory, Client, STATUS_AVAILABLE

__author__ = 'ilyazorin'


_FUCKUP_CLIENTS_MAP = {
    200053: 200500,
    200055: 200646,
    200056: 200252,
    200059: 200188,
    200062: 200448,
    200066: 200377
}


class MenuHandler(ApiHandler):

    def get(self):
        client_id = self.request.get_range('client_id')
        categories = MenuCategory.query().fetch()
        result_dict = {}
        for category in categories:
            result_dict.update(category.dict())
        response = {'menu': result_dict}

        # TODO iOS 1.1 fuckup
        if client_id in _FUCKUP_CLIENTS_MAP:
            logging.warning("fuckup found: %s", client_id)
            client_id = _FUCKUP_CLIENTS_MAP[client_id]
        # TODO END

        client = None
        try:
            client = Client.get_by_id(client_id)
        except:
            pass
        if not client:
            client = Client.create()
            client.put()
            logging.info("issued new client_id: %s", client.key.id())

        response['client_id'] = client.key.id()
        self.render_json(response)
