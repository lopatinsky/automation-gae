from handlers.api.base import ApiHandler
from models import MenuCategory, STATUS_AVAILABLE, MenuItem


def _get_menu():
    return [category.dict() for category in MenuCategory.query(MenuCategory.status == STATUS_AVAILABLE).fetch()]


class MenuHandler(ApiHandler):
    def get(self):
        response = {"menu": _get_menu()}
        self.render_json(response)