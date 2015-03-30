# coding=utf-8

from .base import ApiHandler
from config import config


class DemoInfoHandler(ApiHandler):
    def get(self):
        self.render_json({"demo": config.CARD_BINDING_REQUIRED})
