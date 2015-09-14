from google.appengine.ext import ndb
from methods.rendering import latinize
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.config.config import ORDER_INFO_MODULE

__author__ = 'dvpermyakov'


STRING = 0
NUMBER = 1
TYPE_CHOICES = (STRING, NUMBER)


class Field(ndb.Model):
    title = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True, choices=TYPE_CHOICES)


class ClientModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    extra_fields = ndb.KeyProperty(kind=Field, repeated=True)

    def dict(self):
        return {
            'type': 2,
            'enable': self.status == STATUS_AVAILABLE,
            'fields': [{
                'title': field.title,
                'field': latinize(field.title),
                'type': field.type
            } for field in self.extra_fields]
        }


class OrderModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    extra_fields = ndb.KeyProperty(kind=Field, repeated=True)

    def dict(self):
        return {
            'type': ORDER_INFO_MODULE,
            'enable': self.status == STATUS_AVAILABLE,
            'fields': [{
                'title': field.title,
                'field': latinize(field.title),
                'type': field.type
            } for field in self.extra_fields]
        }
