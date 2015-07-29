from google.appengine.ext import ndb
from models.client import Client

__author__ = 'dvpermyakov'


class IikoCompany(ndb.Model):
    resto_company_id = ndb.IntegerProperty(required=True)


class IikoClient(ndb.Model):
    client = ndb.KeyProperty(kind=Client)