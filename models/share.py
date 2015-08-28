# coding=utf-8
from google.appengine.ext import ndb
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.legal import LegalInfo
from models.menu import MenuItem, SingleModifier
from models.client import Client
from models.payment_types import PAYMENT_TYPE_CHOICES
from models.promo_code import PromoCode

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

    def deactivate(self, namespace):
        from methods.push import send_client_push
        from methods.empatika_promos import register_order
        from methods.empatika_wallet import deposit
        from config import Config
        config = Config.get()
        if config.SHARED_INVITATION_SENDER_ACCUMULATED_POINTS or config.SHARED_INVITATION_SENDER_WALLET_POINTS:
            sender_order_id = "sender_referral_%s" % self.recipient.id()
            register_order(user_id=self.sender.id(), points=config.SHARED_INVITATION_SENDER_ACCUMULATED_POINTS,
                           order_id=sender_order_id)
            deposit(self.sender.id(), config.SHARED_INVITATION_SENDER_WALLET_POINTS * 100, source=sender_order_id)
            sender = self.sender.get()
            text = u'Приглашенный Вами друг сделал заказ. Вам начислены бонусы!'
            header = u'Бонусы!'
            send_client_push(sender, text, header, namespace)
        if config.SHARED_INVITATION_RECIPIENT_ACCUMULATED_POINTS or config.SHARED_INVITATION_RECIPIENT_WALLET_POINTS:
            recipient_order_id = "recipient_referral_%s" % self.recipient.id()
            register_order(user_id=self.recipient.id(), points=config.SHARED_INVITATION_RECIPIENT_ACCUMULATED_POINTS,
                           order_id=recipient_order_id)
            deposit(self.recipient.id(), config.SHARED_INVITATION_RECIPIENT_WALLET_POINTS * 100,
                    source=recipient_order_id)
            recipient = self.recipient.get()
            text = u'Вы сделали заказ по приглашению. Вам начислены бонусы!'
            header = u'Бонусы!'
            send_client_push(recipient, text, header, namespace)
        self.status = self.DONE
        self.put()


class SharedGiftMenuItem(ndb.Model):  # self.id() == item.key.id()
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    item = ndb.KeyProperty(required=True, kind=MenuItem)

    def dict(self):
        return self.item.get().dict()


class ChosenSharedGiftMenuItem(ndb.Model):
    shared_item = ndb.KeyProperty(kind=SharedGiftMenuItem, required=True)
    group_choice_ids = ndb.IntegerProperty(repeated=True)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)


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
    client_id = ndb.IntegerProperty(required=True)         # Who pays for cup
    recipient_name = ndb.StringProperty(required=True)
    recipient_phone = ndb.StringProperty(required=True)
    recipient_id = ndb.IntegerProperty()                   # it is known after perform
    total_sum = ndb.FloatProperty(required=True)
    order_id = ndb.StringProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=PAYMENT_TYPE_CHOICES)
    payment_id = ndb.StringProperty(required=True)
    status = ndb.IntegerProperty(choices=CHOICES, default=READY)

    def perform(self, client, namespace):
        from methods.push import send_client_push
        share = Share.get_by_id(self.share_id)
        share.deactivate()
        self.status = self.PERFORMING
        self.recipient_id = client.key.id()
        self.put()
        sender = Client.get_by_id(self.client_id)
        text = u'%s %s прислал Вам подарок!' % (sender.name, sender.surname)
        header = u'Подарок'
        send_client_push(client, text, header, namespace)

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
        from methods.push import send_client_push
        if self.status == self.READY:
            legal = LegalInfo.query().get()  # TODO find solution for multiple legals
            reverse(legal.alfa_login, legal.alfa_password, self.payment_id)
            share = Share.get_by_id(self.share_id)
            share.deactivate()
            promo_code = self.promo_code.get()
            promo_code.deactivate()
            self.status = self.CANCELED
            self.put()
            sender = Client.get_by_id(self.client_id)
            text = u'Ваш подарок не был получен. Ссылка более не будет активна, а деньги вернутся в ближайшее время.'
            header = u'Отмена подарка'
            send_client_push(sender, text, header, namespace)

    def dict(self):
        from models import Client
        from methods.rendering import timestamp
        item_dict = self.share_item.get().dict()
        item_dict.update({
            'gift_status': self.CHOICES_MAP[self.status]
        })
        recipient_dict = Client.get_by_id(self.recipient_id).dict()
        recipient_dict.update({
            'initial_name': self.recipient_name,
            'initial_phone': self.recipient_phone
        })
        sender_dict = Client.get_by_id(self.client_id).dict()
        return {
            'item': item_dict,
            'recipient': recipient_dict,
            'sender': sender_dict,
            'created': timestamp(self.created),
            'updated': timestamp(self.updated)
        }
