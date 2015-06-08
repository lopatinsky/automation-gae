# coding=utf-8
import datetime
from google.appengine.ext import ndb
from methods import location, working_hours
from models import STATUS_CHOICES, STATUS_AVAILABLE, STATUS_UNAVAILABLE
from models.menu import SingleModifier, MenuItem, GroupModifierChoice
from models.promo import Promo

SELF = 0
IN_CAFE = 1
DELIVERY = 2
PICKUP = 3
DELIVERY_TYPES = [SELF, IN_CAFE, DELIVERY, PICKUP]

DELIVERY_MAP = {
    SELF: u'С собой',
    IN_CAFE: u'В кафе',
    DELIVERY: u'Доставка',
    PICKUP: u'Самовывоз'
}


class Address(ndb.Model):
    lat = ndb.FloatProperty()
    lon = ndb.FloatProperty()
    country = ndb.StringProperty()
    city = ndb.StringProperty()
    street = ndb.StringProperty()
    home = ndb.StringProperty()
    flat = ndb.StringProperty()

    def str(self):
        return u'г. %s, ул. %s, д. %s, кв. %s' % (self.city, self.street, self.home, self.flat)

    def dict(self):
        return {
            'address': {
                'country': self.country,
                'city': self.city,
                'street': self.street,
                'home': self.home,
                'flat': self.flat
            },
            'coordinates': {
                'lon': self.lat,
                'lat': self.lon
            }
        }


class DeliverySlot(ndb.Model):
    MINUTES = 0
    STRINGS = 1
    CHOICES = [MINUTES, STRINGS]
    CHOICES_MAP = {
        MINUTES: u'Минуты',
        STRINGS: u'Без значения'
    }

    name = ndb.StringProperty(required=True)
    slot_type = ndb.IntegerProperty(choices=CHOICES, default=MINUTES)
    value = ndb.IntegerProperty()

    def dict(self):
        return {
            'id': str(self.key.id()),
            'name': self.name
        }


class GeoRib(ndb.LocalStructuredProperty):
    x = ndb.GeoPtProperty(required=True)
    y = ndb.GeoPtProperty(required=True)


class DeliveryZone(ndb.Model):
    address = ndb.LocalStructuredProperty(Address)
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    price = ndb.IntegerProperty(default=0)
    min_sum = ndb.IntegerProperty(default=0)
    geo_ribs = ndb.LocalStructuredProperty(GeoRib, repeated=True)


class DeliveryType(ndb.Model):
    MAX_DAYS = 7
    ONE_DAY_SEC = 86400

    delivery_type = ndb.IntegerProperty(choices=DELIVERY_TYPES)
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_UNAVAILABLE)
    min_time = ndb.IntegerProperty(default=0)
    max_time = ndb.IntegerProperty(default=ONE_DAY_SEC * MAX_DAYS)
    delivery_zones = ndb.KeyProperty(kind=DeliveryZone, repeated=True)
    delivery_slots = ndb.KeyProperty(kind=DeliverySlot, repeated=True)

    @classmethod
    def create(cls, delivery_type):
        delivery = cls(id=delivery_type, delivery_type=delivery_type)
        delivery.put()
        return delivery

    def dict(self):
        return {
            'id': str(self.delivery_type),
            'name': DELIVERY_MAP[self.delivery_type],
            'time_picker_min': self.min_time,
            'time_picker_max': self.max_time,
            'slots': [slot.get().dict() for slot in self.delivery_slots]
        }


class Venue(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    address = ndb.StructuredProperty(Address)
    description = ndb.StringProperty(indexed=False)
    pic = ndb.StringProperty(indexed=False)
    coordinates = ndb.GeoPtProperty(required=True, indexed=False)
    working_days = ndb.StringProperty(indexed=False)
    working_hours = ndb.StringProperty(indexed=False)
    takeout_only = ndb.BooleanProperty(indexed=False, default=False)  # todo: need to remove it
    delivery_types = ndb.LocalStructuredProperty(DeliveryType, repeated=True)
    phone_numbers = ndb.StringProperty(repeated=True, indexed=False)
    holiday_schedule = ndb.StringProperty(indexed=False)
    problem = ndb.StringProperty(indexed=False)
    active = ndb.BooleanProperty(required=True, default=False)
    type_deliveries = ndb.IntegerProperty(repeated=True)
    timezone_offset = ndb.IntegerProperty(default=3)  # hours offset
    stop_lists = ndb.KeyProperty(kind=MenuItem, repeated=True)
    single_modifiers_stop_list = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_choice_modifier_stop_list = ndb.KeyProperty(kind=GroupModifierChoice, repeated=True)
    promo_restrictions = ndb.KeyProperty(kind=Promo, repeated=True)

    def dynamic_info(self):
        items = []
        for item in self.stop_lists:
            item = item.get()
            if item.status != STATUS_AVAILABLE and self.key in item.restrictions:
                continue
            items.append(str(item.key.id()))
        return {
            'stop_list': {
                'items': items,
                'single_modifiers': [str(item.id()) for item in self.single_modifiers_stop_list],
                'group_modifier_choices': [str(item.get().choice_id) for item in self.group_choice_modifier_stop_list]
            }
        }

    def get_delivery_type(self, delivery_type):
        for delivery in self.delivery_types:
            if delivery.delivery_type == delivery_type:
                return delivery

    def dict(self, user_location=None):
        distance = 0
        if user_location:
            distance = location.distance(user_location, self.coordinates)
        dct = {
            'id': str(self.key.id()),
            'distance': distance,
            'title': self.title,
            'address': self.description,
            'pic': self.pic,
            'lat': self.coordinates.lat,
            'lon': self.coordinates.lon,
            'coordinates': str(self.coordinates),
            'is_open': self.is_open(),
            'takeout_only': self.takeout_only,
            'deliveries': [delivery.dict() for delivery in self.delivery_types if delivery.status == STATUS_AVAILABLE],
            'schedule': []
        }
        working_days = self.working_days.split(',')
        working_hours = self.working_hours.split(',')
        for i in xrange(len(working_days)):
            dct['schedule'].append({'days': [int(day) for day in working_days[i]],
                                    'hours': working_hours[i]})
        return dct

    def admin_dict(self):
        return {
            'id': self.key.id(),
            'title': self.title,
            'address': self.description
        }

    def is_open_by_delivery_time(self, delivery_time):
        now = delivery_time + datetime.timedelta(hours=self.timezone_offset)
        return working_hours.check(self.working_days, self.working_hours, now, self.holiday_schedule)

    def is_open(self, minutes_offset=0):
        now = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes_offset)
        return self.is_open_by_delivery_time(now)