from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES
from models.config.config import SUBSCRIPTION

__author__ = 'dvpermyakov'


class SubscriptionModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)

    menu_title = ndb.StringProperty(required=True)
    menu_description = ndb.StringProperty(required=True)
    screen_title = ndb.StringProperty(required=True)
    screen_description = ndb.StringProperty(required=True)

    @classmethod
    def has_module(cls):
        from models.config.config import config
        return config.SUBSCRIPTION_MODULE and config.SUBSCRIPTION_MODULE.status == STATUS_AVAILABLE

    def dict(self):
        return {
            'type': SUBSCRIPTION,
            'info': {
                'menu': {
                    'title': self.menu_title,
                    'description': self.menu_description
                },
                'screen': {
                    'title': self.screen_title,
                    'description': self.screen_description
                }
            }
        }
