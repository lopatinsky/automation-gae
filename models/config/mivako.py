from google.appengine.ext import ndb
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.config.config import MIVAKO_GIFT_MODULE

__author__ = 'dvpermyakov'


class MivakoGiftModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    emails = ndb.StringProperty(repeated=True)
    text = ndb.StringProperty()
    title = ndb.StringProperty()

    def dict(self):
        return {
            'type': MIVAKO_GIFT_MODULE,
            'info': {
                'text': self.text,
                'title': self.title,
            }
        }
