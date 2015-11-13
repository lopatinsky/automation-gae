from google.appengine.ext import ndb
from models import Client, MenuItem

__author__ = 'dvpermyakov'


class Recipient(ndb.Model):
    name = ndb.StringProperty(required=True)
    phone = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class MivakoGift(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    items = ndb.KeyProperty(kind=MenuItem, repeated=True)
    sender = ndb.KeyProperty(kind=Client)
    recipient = ndb.LocalStructuredProperty(Recipient)