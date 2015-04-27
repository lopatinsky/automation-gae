# coding=utf-8

from .base import ApiHandler
from config import config
from models import Promo


class DemoInfoHandler(ApiHandler):
    def get(self):
        self.render_json({"demo": config.CARD_BINDING_REQUIRED})


class PromoInfoHandler(ApiHandler):
    def get(self):
        self.render_json({
            'promos': [promo.dict() for promo in Promo.query().fetch()]
        })