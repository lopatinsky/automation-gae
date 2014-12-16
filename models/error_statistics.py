__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class PaymentErrorsStatistics(ndb.Model):
    data_created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    request_number = ndb.IntegerProperty(default=0, indexed=False)
    total_error_number = ndb.IntegerProperty(default=0, indexed=False)
    serial_error_number = ndb.IntegerProperty(default=0, indexed=False)
    registration_error_number = ndb.IntegerProperty(default=0, indexed=False)
    reverse_error_number = ndb.IntegerProperty(default=0, indexed=False)
    payment_error_number = ndb.IntegerProperty(default=0, indexed=False)
    deposit_error_number = ndb.IntegerProperty(default=0, indexed=False)
    unbind_error_number = ndb.IntegerProperty(default=0, indexed=False)