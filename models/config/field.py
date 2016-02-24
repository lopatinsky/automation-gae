from collections import defaultdict

from google.appengine.ext import ndb
from methods.rendering import latinize
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.config.config import ORDER_INFO_MODULE, NUMBER_OF_PEOPLE_MODULE, CASH_CHANGE_MODULE, CLIENT_INFO_MODULE

__author__ = 'dvpermyakov'

STRING = 0
NUMBER = 1
# NUMBER_PLUS_MINUS = 2  # deprecated
DATE = 3
TYPE_CHOICES = (STRING, NUMBER, DATE)

PAYMENT_RESTRICTION = 0
DELIVERY_TYPE_RESTRICTION = 1
RESTRICTIONS = (PAYMENT_RESTRICTION, DELIVERY_TYPE_RESTRICTION)


class Restriction(ndb.Model):
    field_title = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True, choices=RESTRICTIONS)
    key = ndb.KeyProperty()       # if model has key use it
    value = ndb.StringProperty()  # another way

    def dict(self):
        return {
            'type': self.type,
            'value': self.key.id() if self.key else self.value
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
    enable_number_of_people = ndb.BooleanProperty(default=False)
    enable_change = ndb.BooleanProperty(default=False)

    def _main_dict(self):
        restrictions_dict = defaultdict(list)
        for restriction in self.restrictions:
            restrictions_dict[restriction.field_title].append(restriction.dict())

        groups = defaultdict(list)
        for field in self.extra_fields:
            dct = field.dict()
            dct['restrictions'] = restrictions_dict.get(field.title, [])
            groups[field.group_title].append(dct)
        if groups:
            return {
                'type': ORDER_INFO_MODULE,
                'groups': [{
                    'fields': fields,
                    'group_title': group_title,
                    'group_field': latinize(group_title)
                } for group_title, fields in groups.iteritems()]
            }
        return None

    def dicts(self):
        result = []

        main_dict = self._main_dict()
        if main_dict:
            result.append(main_dict)

        if self.enable_number_of_people:
            result.append({
                'type': NUMBER_OF_PEOPLE_MODULE
            })
        if self.enable_change:
            result.append({
                'type': CASH_CHANGE_MODULE
            })
        return result
