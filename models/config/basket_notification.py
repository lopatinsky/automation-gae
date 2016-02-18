from google.appengine.ext import ndb
from models import STATUS_CHOICES, STATUS_AVAILABLE

__author__ = 'aryabukha'


class BasketNotificationModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    header = ndb.TextProperty()
    text = ndb.TextProperty()
    inactivity_duration = ndb.IntegerProperty(default=1800)  # duration in seconds
    days_since_order = ndb.IntegerProperty(default=0)
