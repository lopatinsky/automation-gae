from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES
from models.client import Client

__author__ = 'dvpermyakov'


class RestoCompany(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    @classmethod
    def get(cls):
        return cls.query(cls.status == STATUS_AVAILABLE).get()


class RestoClient(ndb.Model):
    client = ndb.KeyProperty(kind=Client, required=True)
    resto_customer_id = ndb.StringProperty(required=True)

    @classmethod
    def get(cls, auto_client):
        return cls.query(cls.client == auto_client.key).get()
