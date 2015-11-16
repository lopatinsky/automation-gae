from google.appengine.ext import ndb
from models import STATUS_CHOICES, STATUS_AVAILABLE, Client

__author__ = 'dvpermyakov'


class DoublebCompany(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    test_server = ndb.BooleanProperty(default=False)

    @classmethod
    def get(cls):
        return cls.query(cls.status == STATUS_AVAILABLE).get()


class DoublebClient(ndb.Model):
    client = ndb.KeyProperty(kind=Client, required=True)

    @classmethod
    def get(cls, auto_client):
        return cls.query(cls.client == auto_client.key).get()