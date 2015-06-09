from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES

__author__ = 'dvpermyakov'


class AutomationCompany(ndb.Model):
    namespace = ndb.StringProperty(required=True)
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)