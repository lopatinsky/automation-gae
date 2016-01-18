from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.ext.ndb import transactional

from models import STATUS_UNAVAILABLE, STATUS_AVAILABLE, STATUS_CHOICES
from models.client import Client
from models.legal import LegalInfo
from models.menu import MenuItem
from models.payment_types import PAYMENT_TYPE_CHOICES, CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE

__author__ = 'dvpermyakov'


class WindowMenuItem(ndb.Model):
    ID = 1

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    item = ndb.KeyProperty(kind=MenuItem, required=True)

    @classmethod
    def create(cls, item):
        window_item = cls.get()
        if not window_item:
            window_item = cls(id=cls.ID, item=item)
        return window_item

    @classmethod
    def get(cls):
        return cls.get_by_id(cls.ID)

    def dict(self):
        return self.item.get().dict()


class DayMenuItem(WindowMenuItem):
    pass


class SubscriptionMenuItem(WindowMenuItem):
    pass


class SubscriptionTariff(ndb.Model):
    ID = 1

    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    title = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(required=True)
    amount = ndb.IntegerProperty(required=True)
    duration_seconds = ndb.IntegerProperty(required=True)

    @classmethod
    def get(cls):
        return cls.get_by_id(cls.ID)

    def dict(self):
        return {
            'id': self.key.id(),
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'amount': self.amount,
            'days': int(self.duration_seconds) / 60 / 60 / 24 if self.duration_seconds else 0
        }


class Subscription(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    expiration = ndb.DateTimeProperty(required=True)
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    tariff = ndb.KeyProperty(kind=SubscriptionTariff, required=True)
    client = ndb.KeyProperty(kind=Client, required=True)
    initial_amount = ndb.IntegerProperty(required=True)
    used_cups = ndb.IntegerProperty(required=True, default=0)

    payment_amount = ndb.IntegerProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=PAYMENT_TYPE_CHOICES)
    payment_id = ndb.StringProperty(required=True)
    payment_finalized = ndb.BooleanProperty(required=True, default=False)
    payment_return_time = ndb.DateTimeProperty(required=True)
    payment_legal = ndb.KeyProperty(LegalInfo, required=True)

    @transactional()
    def recover(self, amount):
        self.used_cups -= amount
        self.put()

    @transactional()
    def deduct(self, amount):
        if self.initial_amount - self.used_cups >= amount:
            self.used_cups += amount
            self.put()
            return True
        else:
            return False

    def finalize_payment_if_needed(self):
        from methods import alfa_bank, paypal

        if not self.payment_finalized:
            if self.payment_type_id == CARD_PAYMENT_TYPE:
                legal = self.payment_legal.get()
                alfa_bank.deposit(legal.alfa_login, legal.alfa_password, self.payment_id, 0)
            elif self.payment_type_id == PAYPAL_PAYMENT_TYPE:
                paypal.capture(self.payment_id, self.payment_amount)
            self.payment_finalized = True
            self.put()

    def revert_payment(self):
        from methods import alfa_bank, paypal

        assert self.used_cups == 0

        if self.payment_type_id == CARD_PAYMENT_TYPE:
            legal = self.payment_legal.get()
            alfa_bank.reverse(legal.alfa_login, legal.alfa_password, self.payment_id)
        elif self.payment_type_id == PAYPAL_PAYMENT_TYPE:
            paypal.void(self.payment_id)
        self.close()

    def close(self):
        self.status = STATUS_UNAVAILABLE
        self.put()

    def dict(self):
        return {
            'amount': self.initial_amount - self.used_cups,
            'days': (self.expiration - datetime.utcnow()).days
        }