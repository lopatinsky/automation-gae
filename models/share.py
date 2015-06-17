from google.appengine.ext import ndb
import config
from methods.empatika_promos import register_order
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


class SharedFreeCup(ndb.Model):  # free cup is avail after recipient orders smth and should be deleted after that
    READY = 0
    DONE = 1

    sender = ndb.KeyProperty(required=True, kind=Client)
    recipient = ndb.KeyProperty(required=True, kind=Client)
    share_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.IntegerProperty(choices=[READY, DONE], default=READY)

    def deactivate_cup(self):
        order_id = "referral_%s" % self.recipient.id()
        register_order(user_id=self.sender.id(), points=config.POINTS_PER_CUP, order_id=order_id)
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

    def deactivate_cup(self, client):  # todo: rewrite this
        register_order(user_id=client.key.id(), points=config.POINTS_PER_CUP,
                       order_id=self.order_id)
        share = Share.get_by_id(self.share_id)
        share.deactivate()
        self.status = self.DONE
        self.recipient_id = client.key.id()
        self.put()