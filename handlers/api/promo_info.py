# coding=utf-8
from urlparse import urlparse

from .base import ApiHandler
from models.config.config import config
from models import Promo, GiftMenuItem, STATUS_AVAILABLE, News, Client
from models.specials import STATUS_ACTIVE
from models.share import SharedGiftMenuItem


class PromoInfoHandler(ApiHandler):
    WALLET_TEXT = 'Это ваш личный счет, который пополняется каждый раз, когда вы делаете заказ. ' \
                  'Накопленные баллы можно использовать для оплаты новых заказов.'
    BONUS_TEXT = 'Добавляй позиции в заказ, используя накопленные баллы.'

    def get(self):
        client_id = self.request.get('client_id') or int(self.request.headers.get('Client-Id') or 0)
        if client_id:
            client_id = int(client_id)
            client = Client.get_by_id(client_id)
            if not client:
                self.abort(400)
        gift_items = [gift.dict() for gift in GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).order(GiftMenuItem.points).fetch()]
        share_items = [gift.dict() for gift in SharedGiftMenuItem.query(SharedGiftMenuItem.status == STATUS_AVAILABLE).fetch()] \
            if config.SHARE_GIFT_MODULE and config.SHARE_GIFT_MODULE.status else []
        hostname = urlparse(self.request.url).hostname
        promo_texts = []
        promo_dicts = []
        for promo in sorted(Promo.query_promos(Promo.status == STATUS_AVAILABLE),
                            key=lambda query_promo: -query_promo.priority):
            if not promo.visible or promo.hide_in_list:
                continue
            text = u'%s_%s' % (promo.title.strip() if promo.title else u'',
                               promo.description.strip() if promo.description else u'')
            if text not in promo_texts:
                promo_texts.append(text)
                promo_dicts.append(promo.dict(hostname))
        self.render_json({
            'wallet': {
                'enable': config.WALLET_ENABLED,
                'text': self.WALLET_TEXT
            },
            'promos': promo_dicts,
            'bonuses': {
                'items': gift_items,
                'text': self.BONUS_TEXT
            },
            'shares': {
                'items': share_items
            }
        })


class GiftListHandler(ApiHandler):
    def get(self):
        items = [gift.dict() for gift in sorted(GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).fetch(),
                                                key=lambda item: item.points)]
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