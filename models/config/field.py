from google.appengine.ext import ndb
from methods.rendering import latinize
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.config.config import ORDER_INFO_MODULE, CLIENT_INFO_MODULE

__author__ = 'dvpermyakov'


STRING = 0
NUMBER = 1
NUMBER_PLUS_MINUS = 2
TYPE_CHOICES = (STRING, NUMBER, NUMBER_PLUS_MINUS)

PAYMENT_RESTRICTION = 0
RESTRICTIONS = [PAYMENT_RESTRICTION]


class Restriction(ndb.Model):
    field_title = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True, choices=RESTRICTIONS)
    key = ndb.KeyProperty()

    def dict(self):
        return {
            'type': self.type,
            'value': self.key.id()
        }


class Field(ndb.Model):
    required = ndb.BooleanProperty(default=False)
    title = ndb.StringProperty(required=True)
    group_title = ndb.StringProperty()  # todo: should be required
    type = ndb.IntegerProperty(required=True, choices=TYPE_CHOICES)
    order = ndb.IntegerProperty(required=True)

    def dict(self):
        return {
            'title': self.title,
            'field': latinize(self.title),
            'type': self.type,
            'order': self.order
        }


class ClientModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    extra_fields = ndb.StructuredProperty(Field, repeated=True)

    def dict(self):
        groups = {}
        for field in self.extra_fields:
            if not groups.get(field.group_title):
                groups[field.group_title] = [field.dict()]
            else:
                groups[field.group_title].append(field.dict())
        return {
            'type': CLIENT_INFO_MODULE,
            'groups': [{
                'fields': fields,
                'group_title': group_title,
                'group_field': latinize(group_title)
            } for group_title, fields in groups.iteritems()]
        }


class OrderModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    extra_fields = ndb.StructuredProperty(Field, repeated=True)
    restrictions = ndb.StructuredProperty(Restriction, repeated=True)

    def dict(self):
        return {
            'type': ORDER_INFO_MODULE,
            'fields': [{
                'title': field.title,
                'field': latinize(field.title),
                'type': field.type,
                'restriction': [restriction.dict() for restriction in self.restrictions if restriction.field_title == field.title]
            } for field in self.extra_fields]
        }
