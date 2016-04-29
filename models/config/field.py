from collections import defaultdict

from google.appengine.ext import ndb
from methods.rendering import latinize
from models import STATUS_CHOICES, STATUS_AVAILABLE, STATUS_UNAVAILABLE
from models.config.config import ORDER_INFO_MODULE, NUMBER_OF_PEOPLE_MODULE, CASH_CHANGE_MODULE, CLIENT_INFO_MODULE, \
    CLIENT_INFO_TIP_MODULE

__author__ = 'dvpermyakov'

STRING = 0
NUMBER = 1
# NUMBER_PLUS_MINUS = 2  # deprecated
DATE = 3
CHOICES = 4
CHECKBOX = 5
TYPE_CHOICES = (STRING, NUMBER, DATE, CHOICES, CHECKBOX)

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


class TimeOptions(ndb.Model):
    min_date = ndb.DateTimeProperty()
    max_date = ndb.DateTimeProperty()

    def dict(self):
        return {
            'min_date': self.min_date.strftime("%Y-%m-%d"),
            'max_date': self.max_date.strftime("%Y-%m-%d")
        }


class ChoiceVariantsOptions(ndb.Model):
    variants = ndb.StringProperty(repeated=True)
    default_variant = ndb.IntegerProperty(default=0)

    def dict(self):
        return {
            'variants': self.variants,
            'default_variant': self.default_variant
        }


class Field(ndb.Model):
    required = ndb.BooleanProperty(default=False)
    title = ndb.StringProperty(required=True)
    group_title = ndb.StringProperty()  # todo: should be required
    type = ndb.IntegerProperty(required=True, choices=TYPE_CHOICES)
    order = ndb.IntegerProperty(required=True)
    options = ndb.JsonProperty()

    time_options = ndb.LocalStructuredProperty(TimeOptions, required=False)
    choice_variants_options = ndb.LocalStructuredProperty(ChoiceVariantsOptions, required=False)


    def dict(self):
        options = self.options if self.options else {}

        if self.type == DATE:
            options.update(self.time_options.dict())

        if self.type == CHOICES:
            options.update(self.choice_variants_options.dict())

        return {
            'title': self.title,
            'field': latinize(self.title),
            'type': self.type,
            'order': self.order,
            'options': options,
        }


class ClientTipModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default = STATUS_UNAVAILABLE)
    text = ndb.TextProperty()

    def dict(self):
        return {
            'type': CLIENT_INFO_TIP_MODULE,
            'info': {
                'text': self.text
            }
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
    enable_number_of_people =  ndb.BooleanProperty(default=False)
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
