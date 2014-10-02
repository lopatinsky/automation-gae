from handlers.api.base import ApiHandler
from models import MenuCategory, Client

__author__ = 'ilyazorin'

class MenuHandler(ApiHandler):

    def get(self):
        client_id = self.request.get('client_id')
        categories = MenuCategory.query().fetch()
        response = {'menu': [category.dict() for category in categories]}
        if not client_id:
            client = Client()
            client.put()
            response['client_id'] = client.key.id()
        self.render_json(response)