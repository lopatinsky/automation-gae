from google.appengine.ext import ndb
from config import config
from handlers.api.base import ApiHandler
from handlers.api.registration import perform_registration
from models import MenuCategory, STATUS_AVAILABLE, MenuItem
from methods import versions
import logging

__author__ = 'ilyazorin'


def _get_menu(venue_id):
    return [category.dict(venue_id) for category in MenuCategory.query(MenuCategory.status == STATUS_AVAILABLE).fetch()]


class MenuHandler(ApiHandler):
    def get(self):
        venue_id = self.request.get_range('venue_id')
        response = {"menu": _get_menu(venue_id)}
        self.render_json(response)
