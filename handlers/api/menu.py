from config import config
from handlers.api.base import ApiHandler
from handlers.api.registration import perform_registration
from models import MenuCategory, STATUS_AVAILABLE
from methods import versions

__author__ = 'ilyazorin'


def _get_menu(request):
    old_version = not versions.supports_new_menu(request)
    categories = MenuCategory.query(MenuCategory.status == STATUS_AVAILABLE).fetch()
    result_dict = {}
    for category in categories:
        result_dict.update(category.dict(old_version))
    return result_dict


class MenuHandler(ApiHandler):
    def get(self):
        response = {"menu": _get_menu(self.request)}
        if not versions.supports_registration(self.request):
            response.update(perform_registration(self.request))
            response.update(demo=config.CARD_BINDING_REQUIRED)
        self.render_json(response)
