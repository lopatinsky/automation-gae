# coding=utf-8
from google.appengine.ext import ndb
from webapp2_extras import security

__author__ = 'dvpermyakov'

STATUS_CREATED = 0
STATUS_ACTIVE = 1
STATUS_PERFORMING = 2
STATUS_DONE = 3
STATUS_CANCELLED = 4
PROMO_CODE_STATUS_CHOICES = (STATUS_CREATED, STATUS_ACTIVE, STATUS_DONE, STATUS_CANCELLED)
PROMO_CODE_STATUS_MAP = {
    STATUS_CREATED: u'Создано',
    STATUS_ACTIVE: u'Активно',
    STATUS_PERFORMING: u'Исполнятеся',
    STATUS_DONE: u'Завершено',
    STATUS_CANCELLED: u'Отменено'
}

KIND_SHARE_GIFT = 0
KIND_WALLET = 1
KIND_POINTS = 2
KIND_ORDER_PROMO = 3
PROMO_CODE_KIND_CHOICES = (KIND_SHARE_GIFT, KIND_WALLET, KIND_POINTS, KIND_ORDER_PROMO)
PROMO_CODE_KIND_MAP = {
    KIND_SHARE_GIFT: u'Подари другу',
    KIND_WALLET: u'Баллы на кошелек',
    KIND_POINTS: u'Накопительные баллы',
    KIND_ORDER_PROMO: u'Личные акции'
}


class PromoCode(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    start = ndb.DateTimeProperty(required=True)
    end = ndb.DateTimeProperty(required=True)
    status = ndb.IntegerProperty(choices=PROMO_CODE_STATUS_CHOICES, default=STATUS_CREATED)
    kind = ndb.IntegerProperty(choices=PROMO_CODE_KIND_CHOICES)
    message = ndb.StringProperty()

    @classmethod
    def create(cls, kind, message=None):
        while True:
            key = security.generate_random_string(entropy=256)
            if not cls.get_by_id(key):
                if kind == KIND_SHARE_GIFT:
                    message = u'Вы активировали подарок другу!'
                promo_code = cls(id=key, kind=kind, message=message)
                promo_code.put()
                return promo_code

    def activate(self):
        self.status = STATUS_ACTIVE
        self.put()

    def perform(self):
        self.status = STATUS_PERFORMING
        self.put()

    def deactivate(self):
        self.status = STATUS_DONE
        self.put()

    def cancel(self):
        self.status = STATUS_CANCELLED
        self.put()


class PromoCodeActivation(ndb.Model):
    promo_code = ndb.KeyProperty(required=True)


class PromoCodeGroup(ndb.Model):
    codes = ndb.KeyProperty(kind=PromoCode, repeated=True)