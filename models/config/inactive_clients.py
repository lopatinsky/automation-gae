from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES

__author__ = 'dvpermyakov'


WITHOUT_CONDITIONS = 0
REPEATED_ORDER_CONDITIONS = 1
REPEATED_ORDER_ONE_USE_CONDITION = 2
ORDER_IN_ONE_DAY = 3
CONDITIONS = (WITHOUT_CONDITIONS, REPEATED_ORDER_CONDITIONS, REPEATED_ORDER_ONE_USE_CONDITION, ORDER_IN_ONE_DAY)


class SendingSmsModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    header = ndb.StringProperty(required=True)
    text = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True, choices=CONDITIONS)
    days = ndb.IntegerProperty()
    last_sms = ndb.IntegerProperty(default=14)  # minimal days between two sms sendings
    only_with_cash_back = ndb.BooleanProperty(default=False)
    only_with_points = ndb.BooleanProperty(default=False)
