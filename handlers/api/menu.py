from handlers.api.base import ApiHandler
from models import MenuCategory, Client, STATUS_AVAILABLE

__author__ = 'ilyazorin'


class MenuHandler(ApiHandler):

    def get(self):
        client_id = self.request.get_range('client_id')
        categories = MenuCategory.query().fetch()
        result_dict = {}
        for category in categories:
            result_dict.update(category.dict())
        response = {'menu': result_dict}

        client = None
        try:
            client = Client.get_by_id(client_id)
        except:
            pass
        if not client:
            client = Client.create()
            client.put()

        response['client_id'] = client.key.id()
        self.render_json(response)
