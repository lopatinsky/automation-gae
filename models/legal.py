from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES

__author__ = 'dvpermyakov'


class LegalInfo(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    name = ndb.StringProperty(required=True)
    address = ndb.StringProperty(required=True)
    site = ndb.StringProperty(required=True)
    person_ooo = ndb.StringProperty()  # ooo or ip
    person_ip = ndb.StringProperty()
    contacts = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    inn = ndb.StringProperty()
    kpp = ndb.StringProperty()
    ogrn = ndb.StringProperty()
    ogrnip = ndb.StringProperty(indexed=False)