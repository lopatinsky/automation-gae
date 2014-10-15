from handlers.api.base import ApiHandler
from models import MenuCategory, Client

__author__ = 'ilyazorin'


class MenuHandler(ApiHandler):

    def get(self):
        client_id = self.request.get('client_id')
        categories = MenuCategory.query().fetch()
        result_dict = {}
        for category in categories:
            result_dict.update(category.dict())
        response = {'menu': result_dict}
        if not client_id:
            client = Client.create()
            client.put()
            response['client_id'] = client.key.id()
        else:
            response['client_id'] = client_id
        self.render_json(response)
