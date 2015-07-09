# coding=utf-8
from urlparse import urlparse

from .base import ApiHandler
from config import config
from models import Promo, GiftMenuItem, STATUS_AVAILABLE, News, SharedGift, Client
from models.specials import STATUS_ACTIVE
from models.share import SharedGiftMenuItem


class PromoInfoHandler(ApiHandler):
    WALLET_TEXT = 'Это ваш личный счет, который пополняется каждый раз, когда вы делаете заказ. ' \
                  'Накопленные баллы можно использовать для оплаты новых заказов.'
    BONUS_TEXT = 'Добавляй позиции в заказ, используя накопленные баллы.'

    def get(self):
        client_id = self.request.get('client_id')
        if client_id:
            client_id = int(client_id)
            client = Client.get_by_id(client_id)
            if not client:
                self.abort(400)
            share_gifts = [gift.dict() for gift in SharedGift.query(SharedGift.recipient_id == client_id).fetch()]
        else:
            share_gifts = []
        gift_items = [gift.dict() for gift in GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).fetch()]
        share_items = [gift.dict() for gift in SharedGiftMenuItem.query(SharedGiftMenuItem.status == STATUS_AVAILABLE).fetch()]
        hostname = urlparse(self.request.url).hostname
        self.render_json({
            'wallet': {
                'enable': config.WALLET_ENABLED,
                'text': self.WALLET_TEXT
            },
            'promos': [promo.dict(hostname) for promo in Promo.query(Promo.status == STATUS_AVAILABLE).order(-Promo.priority).fetch()],
            'bonuses': {
                'items': gift_items,
                'text': self.BONUS_TEXT
            },
            'shares': {
                'items': share_items,
                'gifts': share_gifts
            }
        })


class GiftListHandler(ApiHandler):
    def get(self):
        items = [gift.dict() for gift in GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).fetch()]
        self.render_json({
            'items': items
        })


class SharedGiftListHandler(ApiHandler):
    def get(self):
        items = [gift.dict() for gift in SharedGiftMenuItem.query(SharedGiftMenuItem.status == STATUS_AVAILABLE).fetch()]
        self.render_json({
            'items': items
        })


class NewsHandler(ApiHandler):
    def get(self):
        news = News.query(News.status == STATUS_ACTIVE).fetch()
        self.render_json({
            'news': [new.dict() for new in news]
        })