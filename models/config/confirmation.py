from google.appengine.ext import ndb

from models import STATUS_AVAILABLE, STATUS_CHOICES


class SmsConfirmationModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    message = ndb.StringProperty()

    def dict(self):
        return {
            'type': SMS_CONFIRMATION_MODULE,
        }
