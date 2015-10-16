from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES

__author__ = 'dvpermyakov'


WITHOUT_CONDITIONS = 0
REPEATED_ORDER_CONDITIONS = 1
REPEATED_ORDER_ONE_USE_CONDITION = 2
CONDITIONS = (WITHOUT_CONDITIONS, REPEATED_ORDER_CONDITIONS, REPEATED_ORDER_ONE_USE_CONDITION)


class SendingSmsModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    text = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True, choices=CONDITIONS)
    days = ndb.IntegerProperty()
