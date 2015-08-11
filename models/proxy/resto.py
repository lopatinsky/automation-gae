from google.appengine.ext import ndb
from models.client import Client

__author__ = 'dvpermyakov'


class RestoCompany(ndb.Model):
    pass


class RestoClient(ndb.Model):
    client = ndb.KeyProperty(kind=Client, required=True)
