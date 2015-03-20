from google.appengine.ext import ndb
from config import config
from handlers.api.base import ApiHandler
from handlers.api.registration import perform_registration
from models import MenuCategory, STATUS_AVAILABLE, MenuItem
from methods import versions
import logging

__author__ = 'ilyazorin'


def _get_menu():
    return [category.dict() for category in MenuCategory.query(MenuCategory.status == STATUS_AVAILABLE).fetch()]


class MenuHandler(ApiHandler):
    def get(self):
        response = {"menu": _get_menu()}
        self.render_json(response)
