__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class OrderNotificationStatus(ndb.Model):
    order_id = ndb.IntegerProperty(required=True)
    response_success = ndb.BooleanProperty(indexed=False)