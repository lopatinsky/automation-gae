from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES
from models.config.config import GEO_PUSH_MODULE

__author__ = 'dvpermyakov'


class GeoPushModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    text = ndb.StringProperty(required=True)
    head = ndb.StringProperty(required=True)
    days_without_order = ndb.IntegerProperty(required=True)
    days_without_push = ndb.IntegerProperty(required=True)

    def dict(self):
        return {
            'type': GEO_PUSH_MODULE,
            'enable': self.status == STATUS_AVAILABLE,
            'info': {
                'head': self.head,
                'text': self.text,
                'days_without_order': self.days_without_order,
                'days_without_push': self.days_without_push
            }
        }
