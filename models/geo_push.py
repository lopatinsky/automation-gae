from google.appengine.ext import ndb
from models import Client, STATUS_AVAILABLE, STATUS_CHOICES, STATUS_UNAVAILABLE

__author__ = 'dvpermyakov'


class PersonalDailyPromo(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    client = ndb.KeyProperty(kind=Client)

    def deactivate(self):
        self.status = STATUS_UNAVAILABLE
        self.put()

    def recover(self):
        self.status = STATUS_AVAILABLE
        self.put()


class GeoPush(PersonalDailyPromo):
    pass


class LeftBasketPromo(PersonalDailyPromo):
    pass
