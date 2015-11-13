from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.ext.ndb import transactional
from models import STATUS_UNAVAILABLE, STATUS_AVAILABLE, STATUS_CHOICES
from models.client import Client
from models.menu import MenuItem

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
    rest = ndb.IntegerProperty(required=True)

    @transactional()
    def recover(self, amount):
        self.rest += amount
        self.put()

    @transactional()
    def deduct(self, amount):
        if self.rest >= amount:
            self.rest -= amount
            self.put()
            return True
        else:
            return False

    def close(self):
        self.status = STATUS_UNAVAILABLE
        self.put()

    def dict(self):
        return {
            'amount': self.rest,
            'days': (self.expiration - datetime.utcnow()).days
        }