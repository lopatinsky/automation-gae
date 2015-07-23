# coding=utf-8
from google.appengine.ext import ndb
from webapp2_extras import security
from models import Client
from google.appengine.api.namespace_manager import namespace_manager

__author__ = 'dvpermyakov'

STATUS_ACTIVE = 1
STATUS_PERFORMING = 2
STATUS_DONE = 3
PROMO_CODE_STATUS_CHOICES = (STATUS_ACTIVE, STATUS_PERFORMING, STATUS_DONE)
PROMO_CODE_STATUS_MAP = {
    STATUS_ACTIVE: u'Активно',
    STATUS_PERFORMING: u'Исполнятеся',
    STATUS_DONE: u'Завершено',
}

KIND_SHARE_GIFT = 0
KIND_WALLET = 1
KIND_POINTS = 2
KIND_ORDER_PROMO = 3
PROMO_CODE_KIND_CHOICES = (KIND_SHARE_GIFT, KIND_WALLET, KIND_POINTS, KIND_ORDER_PROMO)
PROMO_CODE_KIND_ADMIN = (KIND_WALLET, KIND_POINTS, KIND_ORDER_PROMO)
PROMO_CODE_KIND_MAP = {
    KIND_SHARE_GIFT: u'Подари другу',
    KIND_WALLET: u'Баллы на кошелек',
    KIND_POINTS: u'Накопительные баллы',
    KIND_ORDER_PROMO: u'Личные акции'
}


DEFAULT_MESSAGE_MAP = {
    KIND_SHARE_GIFT: u'Вы активировали подарок другу!',
    KIND_WALLET: u'Вам будут начислены бонусы на личный счет',
    KIND_POINTS: u'Вам будут начисленыы баллы',
    KIND_ORDER_PROMO: u'Вам будет доступна новая акция'
}


class PromoCode(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    value = ndb.IntegerProperty()
    group_id = ndb.IntegerProperty()
    init_amount = ndb.IntegerProperty(required=True)
    amount = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty()
    status = ndb.IntegerProperty(choices=PROMO_CODE_STATUS_CHOICES, default=STATUS_ACTIVE)
    kind = ndb.IntegerProperty(choices=PROMO_CODE_KIND_CHOICES)
    message = ndb.StringProperty()

    @classmethod
    def create(cls, group, kind, amount, value=None, title=None, message=None):
        while True:
            key = security.generate_random_string(length=7)
            if not cls.get_by_id(key):
                if not message:
                    message = DEFAULT_MESSAGE_MAP[kind]
                promo_code = cls(id=key, kind=kind, title=title, amount=amount, init_amount=amount, message=message,
                                 value=value, group_id=group.key.id())
                promo_code.put()
                return promo_code

    def check(self, client):  # use priority for conditions
        if self.status not in [STATUS_ACTIVE, STATUS_PERFORMING]:
            return False, u'Промо код не активен'
        if PromoCodePerforming.query(PromoCodePerforming.client == client.key, PromoCodePerforming.promo_code == self.key).get():
            return False, u'Вы уже активировали этот промо-код'
        return True, None

    @ndb.transactional(xg=True)
    def perform(self, client):  # use only after check()
        performing = PromoCodePerforming(promo_code=self.key, client=client.key, group_id=self.group_id)
        performing.put()
        performing.perform(client)
        self.status = STATUS_PERFORMING
        self.amount -= 1
        self.put()
        if not self.amount:
            self.deactivate()

    def deactivate(self):
        self.status = STATUS_DONE
        self.put()

    def dict(self):
        return {
            'key': self.key.id(),
            'title': self.title,
            'kind': PROMO_CODE_KIND_MAP[self.kind],
            'status': PROMO_CODE_STATUS_MAP[self.status]
        }


class PromoCodeGroup(ndb.Model):
    promo_codes = ndb.KeyProperty(kind=PromoCode, repeated=True)


class PromoCodePerforming(ndb.Model):
    READY_ACTION = 0
    DONE_ACTION = 1
    ACTION_CHOICES = (READY_ACTION, DONE_ACTION)

    created = ndb.DateTimeProperty(auto_now_add=True)
    promo_code = ndb.KeyProperty(kind=PromoCode, required=True)
    group_id = ndb.IntegerProperty(required=True)
    client = ndb.KeyProperty(kind=Client, required=True)
    status = ndb.IntegerProperty(choices=ACTION_CHOICES, default=READY_ACTION)

    def perform(self, client):
        from models.share import SharedGift
        from methods.empatika_wallet import deposit
        from methods.empatika_promos import register_order

        promo_code = self.promo_code.get()
        if promo_code.kind == KIND_SHARE_GIFT:
            gift = SharedGift.query(SharedGift.promo_code == promo_code.key).get()
            gift.deactivate(client, namespace_manager.get_namespace())
        elif promo_code.kind == KIND_WALLET:
            deposit(client.key.id(), promo_code.value * 100, 'promo code %s' % self.promo_code.id())
        elif promo_code.kind == KIND_POINTS:
            register_order(client.key.id(), promo_code.value, 'promo code %s' % self.promo_code.id())
        self.status = self.DONE_ACTION
        self.put()