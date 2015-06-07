# coding=utf-8
from urlparse import urlparse

from .base import ApiHandler
from config import config
from models import Promo, GiftMenuItem, STATUS_AVAILABLE


class PromoInfoHandler(ApiHandler):
    WALLET_TEXT = 'Это ваш личный счет, который пополняется каждый раз, когда вы делаете заказ. ' \
                  'Накопленные баллы можно использовать для оплаты новых заказов.'
    BONUS_TEXT = 'Добавляй позиции в заказ, используя накопленные баллы.'

    def get(self):
        items = [gift.dict() for gift in GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).fetch()]
        hostname = urlparse(self.request.url).hostname
        self.render_json({
            'wallet': {
                'enable': config.WALLET_ENABLED,
                'text': self.WALLET_TEXT
            },
            'promos': [promo.dict(hostname) for promo in Promo.query(Promo.status == STATUS_AVAILABLE).fetch()],
            'bonuses': {
                'items': items,
                'text': self.BONUS_TEXT
            }
        })


class GiftListHandler(ApiHandler):
    def get(self):
        items = [gift.dict() for gift in GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).fetch()]
        self.render_json({
            'items': items
        })