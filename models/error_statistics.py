__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class AlfaBankRequest(ndb.Model):
    data_created = ndb.DateTimeProperty(auto_now_add=True)
    url = ndb.StringProperty(required=True, indexed=False)
    success = ndb.BooleanProperty(required=True, indexed=False)
    error_code = ndb.IntegerProperty(required=True, indexed=False)
    error_message = ndb.StringProperty(indexed=False)


class PaymentErrorsStatistics(object):
    @staticmethod
    def append_request(**kwargs):
        AlfaBankRequest(**kwargs).put_async()

    @staticmethod
    def get_requests(since):
        return AlfaBankRequest.query(AlfaBankRequest.data_created >= since).fetch()
