# coding=utf-8
from google.appengine.ext import ndb
from google.appengine.ext.deferred import deferred
from webapp2_extras import security
from models import Client
from google.appengine.api.namespace_manager import namespace_manager

__author__ = 'dvpermyakov'

STATUS_ACTIVE = 1
STATUS_PERFORMING = 2
STATUS_DONE = 3
PROMO_CODE_STATUS_CHOICES = (STATUS_ACTIVE, STATUS_PERFORMING, STATUS_DONE)
PROMO_CODE_ACTIVE_STATUS_CHOICES = (STATUS_ACTIVE, STATUS_PERFORMING)
PROMO_CODE_STATUS_MAP = {
    STATUS_ACTIVE: u'Активно',
    STATUS_PERFORMING: u'Исполнятеся',
    STATUS_DONE: u'Завершено',
}

KIND_SHARE_GIFT = 0
KIND_WALLET = 1
KIND_POINTS = 2
KIND_ORDER_PROMO = 3
KIND_ALL_TIME_HACK = 4
KIND_SHARE_INVITATION = 5
PROMO_CODE_KIND_CHOICES = (KIND_SHARE_GIFT, KIND_WALLET, KIND_POINTS, KIND_ORDER_PROMO, KIND_ALL_TIME_HACK,
                           KIND_SHARE_INVITATION)
PROMO_CODE_KIND_ADMIN = (KIND_WALLET, KIND_POINTS, KIND_ORDER_PROMO, KIND_ALL_TIME_HACK)
PROMO_CODE_KIND_MAP = {
    KIND_SHARE_GIFT: u'Подари другу',
    KIND_WALLET: u'Баллы на кошелек',
    KIND_POINTS: u'Накопительные баллы',
    KIND_ORDER_PROMO: u'Личные акции',
    KIND_ALL_TIME_HACK: u'Заказ в любое время',
    KIND_SHARE_INVITATION: u'Пригласи друга'
}


DEFAULT_MESSAGE_MAP = {
    KIND_SHARE_GIFT: u'Вы активировали подарок другу!',
    KIND_WALLET: u'Вам будут начислены бонусы на личный счет',
    KIND_POINTS: u'Вам будут начисленыы баллы',
    KIND_ORDER_PROMO: u'Вам будет доступна новая акция',
    KIND_ALL_TIME_HACK: u'Если Вы не разработчик приложения, обратитесь в службу поддержки',
    KIND_SHARE_INVITATION: u'Вы активировали приглашение друга. Сделайте заказ и получите бонусы!'
}


class PromoCode(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    persist = ndb.BooleanProperty(default=False)
    value = ndb.IntegerProperty()
    group_id = ndb.IntegerProperty()
    init_amount = ndb.IntegerProperty(required=True)
    amount = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty()
    status = ndb.IntegerProperty(choices=PROMO_CODE_STATUS_CHOICES, default=STATUS_ACTIVE)
    kind = ndb.IntegerProperty(choices=PROMO_CODE_KIND_CHOICES)
    message = ndb.StringProperty()

    @classmethod
    def create(cls, group, kind, amount, value=None, title=None, message=None, promo_code_key=None, persist=False):
        while True:
            key = security.generate_random_string(length=7).lower() if not promo_code_key else promo_code_key
            if not cls.get_by_id(key):
                if not message:
                    message = DEFAULT_MESSAGE_MAP[kind]
                promo_code = cls(id=key, kind=kind, title=title, amount=amount, init_amount=amount, message=message,
                                 value=value, group_id=group.key.id(), persist=persist)
                promo_code.put()
                return promo_code
            promo_code_key = None

    def check(self, client):  # use priority for conditions
        from models.share import Share, SharedPromo
        if self.status not in PROMO_CODE_ACTIVE_STATUS_CHOICES:
            return False, u'Промо код не активен'
        if PromoCodePerforming.query(PromoCodePerforming.client == client.key, PromoCodePerforming.promo_code == self.key).get():
            return False, u'Вы уже активировали этот промо-код'
        if self.kind == KIND_SHARE_INVITATION:
            share = Share.query(Share.promo_code == self.key).get()
            promo = SharedPromo.query(SharedPromo.recipient == client.key).get()
            if client.key.id() == share.sender.id():
                return False, u'Невозможно перейти по собственному промо-коду'
            if promo:
                return False, u'Вы уже активировали приглашение!'
        return True, None

    def perform(self, client):  # use only after check()
        performing = PromoCodePerforming(promo_code=self.key, client=client.key, group_id=self.group_id)
        performing.put()
        deferred.defer(performing.perform, client)
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
    PROCESSING_ACTION = 2
    IN_ORDER = 3
    ACTION_CHOICES = (READY_ACTION, PROCESSING_ACTION, IN_ORDER, DONE_ACTION)

    created = ndb.DateTimeProperty(auto_now_add=True)
    promo_code = ndb.KeyProperty(kind=PromoCode, required=True)
    group_id = ndb.IntegerProperty(required=True)
    client = ndb.KeyProperty(kind=Client, required=True)
    status = ndb.IntegerProperty(choices=ACTION_CHOICES, default=READY_ACTION)

    def perform(self, client):
        from models.share import SharedGift, Share, SharedPromo
        from methods.empatika_wallet import deposit
        from methods.empatika_promos import register_order

        promo_code = self.promo_code.get()
        if promo_code.kind == KIND_SHARE_GIFT:
            gift = SharedGift.query(SharedGift.promo_code == promo_code.key).get()
            gift.perform(client, namespace_manager.get_namespace())
            self.status = self.PROCESSING_ACTION
        elif promo_code.kind == KIND_WALLET:
            deposit(client.key.id(), promo_code.value * 100, 'promo code %s' % self.promo_code.id())
            self.status = self.DONE_ACTION
        elif promo_code.kind == KIND_POINTS:
            register_order(client.key.id(), promo_code.value, 'promo code %s' % self.promo_code.id())
            self.status = self.DONE_ACTION
        elif promo_code.kind == KIND_ORDER_PROMO:
            self.status = self.PROCESSING_ACTION
        elif promo_code.kind == KIND_ALL_TIME_HACK:
            self.status = self.PROCESSING_ACTION
        elif promo_code.kind == KIND_SHARE_INVITATION:
            share = Share.query(Share.promo_code == promo_code.key).get()
            promo = SharedPromo.query(SharedPromo.recipient == client.key).get()
            if client.key.id() != share.sender.id() and not promo:
                SharedPromo(sender=share.sender, recipient=client.key, share_id=share.key.id()).put()
        else:
            self.status = self.DONE_ACTION
        self.put()

    def put_in_order(self):
        if self.status == self.PROCESSING_ACTION:
            self.status = self.IN_ORDER
            self.put()

    def recover(self):
        if self.status == self.IN_ORDER:
            self.status = self.PROCESSING_ACTION
            self.put()

    def close(self):
        self.status = self.DONE_ACTION
        self.put()
