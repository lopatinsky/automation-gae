from google.appengine.ext import ndb

from models import STATUS_CHOICES, STATUS_UNAVAILABLE
from models.config.config import CUSTOM_SECTIONS_MODULE


class CustomSection(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    url = ndb.StringProperty(required=True, indexed=False)

    def dict(self):
        return {
            'title': self.title,
            'url': self.url
        }


class CustomSectionsModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_UNAVAILABLE)
    sections = ndb.LocalStructuredProperty(CustomSection, repeated=True)

    def dict(self):
        return {
            'type': CUSTOM_SECTIONS_MODULE,
            'sections': [s.dict() for s in self.sections]
        }
