from config import config
from handlers.api.base import ApiHandler
from handlers.api.registration import perform_registration
from models import MenuCategory, STATUS_AVAILABLE, MenuItem
from methods import versions
import logging

__author__ = 'ilyazorin'


def _get_menu():
    result = []
    for category in MenuCategory.query().fetch():
        result.append({
            'info': {
                'category_id': category.key.id(),
                'title': category.title,
                'status': category.status,
            },
            'items': [item.get().dict() for item in category.menu_items]
        })
    return result


class MenuHandler(ApiHandler):
    def get(self):
        response = {"menu": _get_menu()}
        self.render_json(response)
