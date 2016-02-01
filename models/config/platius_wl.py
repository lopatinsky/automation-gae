from google.appengine.ext import ndb

from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.config.config import PLATIUS_WHITE_LABEL_MODULE


class PlatiusWhiteLabelModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    app_key = ndb.StringProperty()

    def dict(self):
        return {
            'type': PLATIUS_WHITE_LABEL_MODULE
        }
