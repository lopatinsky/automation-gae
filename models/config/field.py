from google.appengine.ext import ndb
from methods.rendering import latinize
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.config.config import ORDER_INFO_MODULE, CLIENT_INFO_MODULE

__author__ = 'dvpermyakov'


STRING = 0
NUMBER = 1
NUMBER_PLUS_MINUS = 2
TYPE_CHOICES = (STRING, NUMBER, NUMBER_PLUS_MINUS)


class Field(ndb.Model):
    title = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True, choices=TYPE_CHOICES)
    order = ndb.IntegerProperty(required=True)


class ClientModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    extra_fields = ndb.StructuredProperty(Field, repeated=True)

    def dict(self):
        return {
            'type': CLIENT_INFO_MODULE,
            'enable': self.status == STATUS_AVAILABLE,
            'fields': [{
                'title': field.title,
                'field': latinize(field.title),
                'type': field.type,
                'order': field.order
            } for field in sorted(self.extra_fields, key=lambda field: field.order)]
        }


class OrderModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    extra_fields = ndb.StructuredProperty(Field, repeated=True)

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
