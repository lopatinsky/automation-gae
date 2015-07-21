# coding=utf-8
from google.appengine.api.taskqueue import taskqueue
from google.appengine.ext import ndb
from webapp2_extras import security
from models import Client

__author__ = 'dvpermyakov'

STATUS_CREATED = 0
STATUS_ACTIVE = 1
STATUS_PERFORMING = 2
STATUS_DONE = 3
STATUS_CANCELLED = 4
PROMO_CODE_STATUS_CHOICES = (STATUS_CREATED, STATUS_ACTIVE, STATUS_PERFORMING, STATUS_DONE, STATUS_CANCELLED)
PROMO_CODE_HISTORY_STATUS_CHOICES = (STATUS_PERFORMING, STATUS_DONE)
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
    client = ndb.KeyProperty(kind=Client)  # who activates promo code

    @classmethod
    def create(cls, start, end, kind, message=None):
        while True:
            key = security.generate_random_string(entropy=256)
            if not cls.get_by_id(key):
                if kind == KIND_SHARE_GIFT:
                    message = u'Вы активировали подарок другу!'
                promo_code = cls(id=key, start=start, end=end, kind=kind, message=message)
                promo_code.put()
                taskqueue.add(url='/task/promo_code/start', method='POST', eta=start, params={
                    'code_id': promo_code.key.id()
                })
                taskqueue.add(url='/task/promo_code/close', method='POST', eta=end, params={
                    'code_id': promo_code.key.id()
                })
                return promo_code

    def activate(self):
        self.status = STATUS_ACTIVE
        self.put()

    def perform(self, client):
        self.client = client.key
        self.status = STATUS_PERFORMING
        self.put()
        if self.kind in [KIND_SHARE_GIFT, KIND_WALLET]:
            self.deactivate()

    def deactivate(self):
        self.status = STATUS_DONE
        self.put()

    def cancel(self):
        self.status = STATUS_CANCELLED
        self.put()

    def dict(self):
        return {
            'title': PROMO_CODE_KIND_MAP[self.kind],
            'key': self.id,
            'status': PROMO_CODE_STATUS_MAP[self.status]
        }


class PromoCodeDeposit(ndb.Model):
    READY = 0
    DONE = 1
    CHOICES = (READY, DONE)

    promo_code = ndb.KeyProperty(kind=PromoCode, required=True)
    status = ndb.IntegerProperty(choices=CHOICES, default=READY)
    amount = ndb.IntegerProperty(required=True)  # в рублях

    def deposit(self, client):
        from methods.empatika_wallet import deposit
        deposit(client.key.id(), self.amount * 100, 'promo code %s' % self.promo_code.id())
        self.status = self.DONE
        self.put()
        promo_code = self.promo_code.get()
        promo_code.perform(client)