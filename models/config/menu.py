# coding=utf-8
from google.appengine.ext import ndb
from models import STATUS_CHOICES, STATUS_AVAILABLE, MenuItem, STATUS_UNAVAILABLE
from models.config.config import REMAINDERS_MODULE

__author__ = 'dvpermyakov'


HIT_SEQUENCE_NUMBER = 1


class MenuFrameModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    @classmethod
    def has_module(cls):
        from models.config.config import Config
        config = Config.get()
        module = config.MENU_FRAME_MODULE
        return module and module.status == STATUS_AVAILABLE


class HitModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    consider_days = ndb.IntegerProperty(default=30)
    items = ndb.KeyProperty(kind=MenuItem, repeated=True)
    cunning_items = ndb.KeyProperty(kind=MenuItem, repeated=True)
    max_item_amount = ndb.IntegerProperty(default=10)
    min_item_rating = ndb.FloatProperty(default=0)
    title = ndb.StringProperty(default=u'Хиты')
    picture = ndb.StringProperty()

    def get_items(self):
        items = []
        for item in self.items:
            item = item.get()
            item.sequence_number = int((1.0 - item.rating) * 100)
            if item.status == STATUS_UNAVAILABLE:
                continue
            if item.status == STATUS_UNAVAILABLE:
                continue
            items.append(item)
        return items


class RemaindersModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    @classmethod
    def has_module(cls):
        from models.config.config import Config, RESTO_APP
        config = Config.get()
        module = config.REMAINDERS_MODULE
        return module and module.status == STATUS_AVAILABLE and config.APP_KIND == RESTO_APP

    def dict(self):
        return {
            'type': REMAINDERS_MODULE
        }
