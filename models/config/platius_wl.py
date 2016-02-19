from google.appengine.ext import ndb

from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.config.config import PLATIUS_WHITE_LABEL_MODULE


class PlatiusWhiteLabelModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    app_key = ndb.StringProperty()

    about_title = ndb.StringProperty(required=True)
    about_description = ndb.StringProperty(required=True)

    def dict(self):
        return {
            'type': PLATIUS_WHITE_LABEL_MODULE,
            'info': {
                'about': {
                    'title': self.about_title,
                    'description': self.about_description
                }
            }
        }
