from google.appengine.ext import ndb

__author__ = 'dvpermyakov'


class LegalInfo(ndb.Model):
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