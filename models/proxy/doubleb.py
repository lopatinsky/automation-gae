from google.appengine.ext import ndb
from models import STATUS_CHOICES, STATUS_AVAILABLE

__author__ = 'dvpermyakov'


class DoublebCompany(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    test_server = ndb.BooleanProperty(default=False)

    @classmethod
    def get(cls):
        return cls.query(cls.status == STATUS_AVAILABLE).get()