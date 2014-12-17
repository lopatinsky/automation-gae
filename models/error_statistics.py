__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class AlfaBankRequest(ndb.Model):
    data_created = ndb.DateTimeProperty(auto_now_add=True)
    url = ndb.StringProperty(required=True, indexed=False)
    success = ndb.BooleanProperty(required=True, indexed=False)


class PaymentErrorsStatistics(ndb.Model):
    data_created = ndb.DateTimeProperty(auto_now_add=True)
    alfa_bank_requests = ndb.StructuredProperty(AlfaBankRequest, repeated=True)