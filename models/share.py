from google.appengine.ext import ndb
from config import Config
from methods.empatika_promos import register_order
from methods.empatika_wallet import deposit
from models import MenuItem, STATUS_CHOICES, STATUS_AVAILABLE
from models.client import Client
from models.payment_types import PAYMENT_TYPE_CHOICES

__author__ = 'dvpermyakov'


class Share(ndb.Model):
    from methods.branch_io import FEATURE_CHOICES

    ACTIVE = 0
    INACTIVE = 1

    sender = ndb.KeyProperty(required=True, kind=Client)
    share_type = ndb.IntegerProperty(required=True, choices=FEATURE_CHOICES)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    status = ndb.IntegerProperty(default=ACTIVE)
    urls = ndb.StringProperty(repeated=True)

    def deactivate(self):
        self.status = self.INACTIVE
        self.put()


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

    def deactivate(self):
        config = Config.get()
        sender_order_id = "sender_referral_%s" % self.recipient.id()
        register_order(user_id=self.sender.id(), points=config.SHARED_INVITATION_SENDER_ACCUMULATED_POINTS,
                       order_id=sender_order_id)
        deposit(self.sender.id(), config.SHARED_INVITATION_SENDER_WALLET_POINTS, source=sender_order_id)
        recipient_order_id = "recipient_referral_%s" % self.recipient.id()
        register_order(user_id=self.sender.id(), points=config.SHARED_INVITATION_RECIPIENT_ACCUMULATED_POINTS,
                       order_id=recipient_order_id)
        deposit(self.sender.id(), config.SHARED_INVITATION_RECIPIENT_WALLET_POINTS, source=recipient_order_id)
        self.status = self.DONE
        self.put()


class SharedGiftMenuItem(ndb.Model):  # self.id() == item.key.id()
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    item = ndb.KeyProperty(required=True, kind=MenuItem)

    def dict(self):
        return self.item.get().dict()


class SharedGift(ndb.Model):
    READY = 0
    DONE = 1
    CANCELED = 2
    CHOICES = [READY, DONE]

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    share_id = ndb.IntegerProperty(required=True)
    share_item = ndb.KeyProperty(required=True, kind=SharedGiftMenuItem)
    client_id = ndb.IntegerProperty(required=True)         # Who pays for cup
    recipient_name = ndb.StringProperty(required=True)
    recipient_phone = ndb.StringProperty(required=True)
    recipient_id = ndb.IntegerProperty()                   # it is known after deactivate
    total_sum = ndb.IntegerProperty(required=True)
    order_id = ndb.StringProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=PAYMENT_TYPE_CHOICES)
    payment_id = ndb.StringProperty(required=True)
    status = ndb.IntegerProperty(choices=CHOICES, default=READY)

    def deactivate(self, client):
        share = Share.get_by_id(self.share_id)
        share.deactivate()
        self.status = self.DONE
        self.recipient_id = client.key.id()
        self.put()

    def cancel(self):
        from methods.alfa_bank import reverse

        if self.status == self.READY:
            reverse(self.payment_id)
            share = Share.get_by_id(self.share_id)
            share.deactivate()
            self.status = self.CANCELED
            self.put()

    def dict(self):
        return self.share_item.get().dict()