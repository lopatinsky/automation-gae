from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES

__author__ = 'dvpermyakov'


class ReviewModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    wait_seconds = ndb.IntegerProperty(default=1200)
