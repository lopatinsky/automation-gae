# coding=utf-8
from google.appengine.ext import ndb

from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.legal import LegalInfo
from models.menu import MenuItem, SingleModifier
from models.client import Client
from models.payment_types import PAYMENT_TYPE_CHOICES
from models.promo_code import PromoCode
from models.push import SimplePush

__author__ = 'dvpermyakov'


class ChannelUrl(ndb.Model):
    url = ndb.StringProperty(required=True)
    channel = ndb.IntegerProperty(required=True)

    def dict(self):
        return {
            'url': self.url,
            'channel': self.channel
        }


class Share(ndb.Model):
    from methods.branch_io import FEATURE_CHOICES

    INACTIVE = 0
    ACTIVE = 1
    STATUS_CHOICES = (ACTIVE, INACTIVE)

    sender = ndb.KeyProperty(required=True, kind=Client)
    share_type = ndb.IntegerProperty(required=True, choices=FEATURE_CHOICES)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=ACTIVE)
    channel_urls = ndb.LocalStructuredProperty(ChannelUrl, repeated=True)
    promo_code = ndb.KeyProperty(kind=PromoCode)

    def deactivate(self):
        self.status = self.INACTIVE
        self.put()

    def dict(self):
        from methods.rendering import timestamp

        return {
            'sender': self.sender.get().dict(),
            'created': timestamp(self.created),
            'updated': timestamp(self.updated),
            'status': self.status
        }


class SharedPromo(ndb.Model):
    READY = 0
    DONE = 1

    sender = ndb.KeyProperty(required=True, kind=Client)
    recipient = ndb.KeyProperty(required=True, kind=Client)
    share_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.IntegerProperty(choices=[READY, DONE], default=READY)
    accumulated_points = ndb.IntegerProperty()
    wallet_points = ndb.IntegerProperty()

    sender_promo_success = ndb.BooleanProperty(default=False)
    recipient_promo_success = ndb.BooleanProperty(default=False)

    def deactivate(self, namespace):
        from methods.empatika_promos import register_order
        from methods.empatika_wallet import deposit
        from models.config.config import config

        module = config.SHARE_INVITATION_MODULE
        if module.sender_accumulated_points or module.sender_wallet_points:
            sender_order_id = "sender_referral_%s" % self.recipient.id()
            if module.sender_accumulated_points:
                register_order(user_id=self.sender.id(), points=module.sender_accumulated_points,
                               order_id=sender_order_id)
            if module.sender_wallet_points:
                deposit(self.sender.id(), module.sender_wallet_points * 100, source=sender_order_id)
            sender = self.sender.get()
            text = u'Приглашенный Вами друг сделал заказ. Вам начислены бонусы!'
            header = u'Бонусы!'
            SimplePush(text, False, text, header, sender, namespace).send()
        if module.recipient_accumulated_points or module.recipient_wallet_points:
            recipient_order_id = "recipient_referral_%s" % self.recipient.id()
            if module.recipient_accumulated_points:
                register_order(user_id=self.recipient.id(), points=module.recipient_accumulated_points,
                               order_id=recipient_order_id)
            if module.recipient_wallet_points:
                deposit(self.recipient.id(), module.recipient_wallet_points * 100,
                        source=recipient_order_id)
            recipient = self.recipient.get()
            text = u'Вы сделали заказ по приглашению. Вам начислены бонусы!'
            header = u'Бонусы!'
            SimplePush(text, False, text, header, recipient, namespace).send()
        self.status = self.DONE
        self.put()


class SharedGiftMenuItem(ndb.Model):  # self.id() == item.key.id()
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    item = ndb.KeyProperty(required=True, kind=MenuItem)

    def dict(self):
        from models.menu import MenuItem

        return MenuItem.get(product_id=self.item.id()).dict()


class ChosenSharedGiftMenuItem(ndb.Model):
    shared_item = ndb.KeyProperty(kind=SharedGiftMenuItem, required=True)
    group_choice_ids = ndb.IntegerProperty(repeated=True)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)

    def dict(self):
        return self.shared_item.get().dict()


class SharedGift(ndb.Model):
    READY = 0
    DONE = 1
    CANCELED = 2
    PERFORMING = 3
    IN_ORDER = 4
    CHOICES = (READY, PERFORMING, IN_ORDER, DONE, CANCELED)
    CHOICES_MAP = {
        READY: u'Оплачено',
        PERFORMING: u'Получено',
        IN_ORDER: u'Заказан',
        DONE: u'Выдан',
        CANCELED: u'Отменено'
    }

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    promo_code = ndb.KeyProperty(kind=PromoCode)
    share_id = ndb.IntegerProperty(required=True)
    share_items = ndb.KeyProperty(kind=ChosenSharedGiftMenuItem, repeated=True)
    client_id = ndb.IntegerProperty(required=True)  # Who pays for cup
    recipient_name = ndb.StringProperty(required=True)
    recipient_phone = ndb.StringProperty(required=True)
    recipient_id = ndb.IntegerProperty()  # it is known after perform
    total_sum = ndb.FloatProperty(required=True)
    order_id = ndb.StringProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=PAYMENT_TYPE_CHOICES)
    payment_id = ndb.StringProperty(required=True)
    status = ndb.IntegerProperty(choices=CHOICES, default=READY)

    def perform(self, client, namespace):
        share = Share.get_by_id(self.share_id)
        share.deactivate()
        self.status = self.PERFORMING
        self.recipient_id = client.key.id()
        self.put()
        sender = Client.get(self.client_id)
        text = u'%s %s прислал Вам подарок!' % (sender.name, sender.surname)
        header = u'Подарок'
        SimplePush(text, False, text, header, sender, namespace).send()

    def put_in_order(self):
        if self.status == self.PERFORMING:
            self.status = self.IN_ORDER
            self.put()

    def deactivate(self):
        if self.status == self.IN_ORDER:
            self.status = self.DONE
            self.put()

    def recover(self):
        if self.status == self.IN_ORDER:
            self.status = self.PERFORMING
            self.put()

    def cancel(self, namespace):
        from methods.alfa_bank import reverse

        if self.status == self.READY:
            legal = LegalInfo.query().get()  # TODO find solution for multiple legals
            reverse(legal.alfa_login, legal.alfa_password, self.payment_id)
            share = Share.get_by_id(self.share_id)
            share.deactivate()
            promo_code = self.promo_code.get()
            promo_code.deactivate()
            self.status = self.CANCELED
            self.put()
            sender = Client.get(self.client_id)
            text = u'Ваш подарок не был получен. Ссылка более не будет активна, а деньги вернутся в ближайшее время.'
            header = u'Отмена подарка'
            SimplePush(text, False, text, header, sender, namespace).send()

    def dict(self):
        from models import Client
        from models.config.config import config
        from methods.rendering import timestamp

        item_dicts = [si.get().dict() for si in self.share_items]

        if self.recipient_id:
            recipient_dict = Client.get(self.recipient_id).dict()
        else:
            recipient_dict = {}
        recipient_dict.update({
            'initial_name': self.recipient_name,
            'initial_phone': self.recipient_phone
        })

        sender = Client.get(self.client_id)
        sender_dict = sender.dict()

        share = Share.get_by_id(self.share_id)
        text = u'Дарю тебе подарок в приложении %s! Установи его: %s или введи в нем промо-код %s' % \
               (config.APP_NAME, share.channel_urls[0].url, self.promo_code.id())

        return {
            'items': item_dicts,
            'recipient': recipient_dict,
            'sender': sender_dict,
            'status': self.status,
            'sms_text': text,
            'created': timestamp(self.created),
            'updated': timestamp(self.updated)
        }
