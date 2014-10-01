from handlers.api.base import ApiHandler
from models import MenuCategory

__author__ = 'ilyazorin'

class MenuHandler(ApiHandler):

    def get(self):
        categories = MenuCategory.query().fetch()
        #TODO client_id
        self.render_json({'menu': [category.dict() for category in categories]})