# coding=utf-8
from datetime import datetime, timedelta
import logging
import random
from google.appengine.ext import ndb
from methods import location, working_hours, fastcounter
from models import STATUS_CHOICES, STATUS_AVAILABLE, STATUS_UNAVAILABLE, MenuCategory
from models.legal import LegalInfo
from models.menu import SingleModifier, MenuItem, GroupModifierChoice
from models.promo import Promo
from models.schedule import Schedule, DaySchedule
from models.payment_types import PaymentType

SELF = 0
IN_CAFE = 1
DELIVERY = 2
PICKUP = 3
DELIVERY_TYPES = (SELF, IN_CAFE, DELIVERY, PICKUP)

DELIVERY_MAP = {
    SELF: u'С собой',
    IN_CAFE: u'В кафе',
    DELIVERY: u'Доставка',
    PICKUP: u'Самовывоз'
}

DELIVERY_WHAT_MAP = {
    SELF: u'с собой',
    IN_CAFE: u'в кафе',
    DELIVERY: u'на доставку',
    PICKUP: u'при самовывозе'
}


class Address(ndb.Model):
    lat = ndb.FloatProperty()
    lon = ndb.FloatProperty()
    country = ndb.StringProperty()
    city = ndb.StringProperty()
    street = ndb.StringProperty()
    area = ndb.StringProperty()  # районы (not district, district is округ по-русски)
    home = ndb.StringProperty()
    flat = ndb.StringProperty()
    comment = ndb.StringProperty()

    def str(self):
        address_str = u''
        if self.city:
            address_str += u'г. %s,' % self.city
        if self.street:
            address_str += u'ул. %s,' % self.street
        if self.home:
            address_str += u'д. %s' % self.home
        if self.flat:
            address_str += u', кв. %s' % self.flat
        if self.comment:
            address_str += u' (%s)' % self.comment
        return address_str

    def dict(self):
        return {
            'formatted_address': self.str(),
            'address': {
                'country': self.country,
                'city': self.city,
                'street': self.street,
                'home': self.home,
                'flat': self.flat
            },
            'coordinates': {
                'lon': self.lon,
                'lat': self.lat
            },
            'comment': self.comment
        }


class DeliverySlot(ndb.Model):
    MINUTES = 0
    STRINGS = 1
    HOURS_FROM_MIDNIGHT = 2
    CHOICES = (MINUTES, STRINGS, HOURS_FROM_MIDNIGHT)
    CHOICES_MAP = {
        MINUTES: u'Минуты',
        STRINGS: u'Без значения',
        HOURS_FROM_MIDNIGHT: u'Часы от полуночи'
    }

    name = ndb.StringProperty(required=True)
    slot_type = ndb.IntegerProperty(choices=CHOICES, default=MINUTES)
    default = ndb.BooleanProperty(default=False)
    value = ndb.IntegerProperty()

    def dict(self):
        return {
            'id': str(self.key.id()),
            'name': self.name,
            'default': self.default
        }


class GeoPtProxy(ndb.GeoPt):
    @staticmethod
    def square(a, b, c):
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

    @property
    def x(self):
        return self.lat

    @property
    def y(self):
        return self.lon


class GeoRib(ndb.Model):
    point1 = ndb.GeoPtProperty(required=True)
    point2 = ndb.GeoPtProperty(required=True)


class DeliveryZone(ndb.Model):
    CITY = 0
    DISTRICT = 1
    ZONE = 2
    DEFAULT = 3
    NEAREST = 4
    RADIUS = 5
    SEARCH_TYPES = (CITY, DISTRICT, ZONE, DEFAULT, NEAREST, RADIUS)
    SEARCH_MAP = {
        CITY: u'По городу',
        DISTRICT: u'По району',
        ZONE: u'Собственная зона',
        DEFAULT: u'По умолчанию',
        NEAREST: u'Ближайшая',
        RADIUS: u'Радиус'
    }
    search_type = ndb.IntegerProperty(choices=SEARCH_TYPES, default=CITY)
    value = ndb.IntegerProperty()
    sequence_number = ndb.IntegerProperty()
    address = ndb.LocalStructuredProperty(Address)
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    price = ndb.IntegerProperty(default=0)
    min_sum = ndb.IntegerProperty(default=0)
    comment = ndb.StringProperty()
    geo_ribs = ndb.LocalStructuredProperty(GeoRib, repeated=True)

    @classmethod
    def get(cls, zone_key):
        from models.config.config import config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.company import get_delivery_zone
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(zone_key.id())
        elif app_kind == RESTO_APP:
            return get_delivery_zone(zone_key)

    @staticmethod
    def generate_sequence_number():
        fastcounter.incr("delivery_zones", delta=100, update_interval=1)
        return fastcounter.get_count("delivery_zones") + random.randint(1, 100)

    @staticmethod
    def get_zones_in_order():
        return sorted([zone for zone in DeliveryZone.query().fetch()],
                      key=lambda zone: zone.sequence_number)

    def get_previous(self):
        zones = self.get_zones_in_order()
        index = zones.index(self)
        if index == 0:
            return None
        else:
            return zones[index - 1]

    def get_next(self):
        zones = self.get_zones_in_order()
        index = zones.index(self)
        if index == len(zones) - 1:
            return None
        else:
            return zones[index + 1]

    @property
    def polygon(self):
        points = []
        for rib in self.geo_ribs:
            points.append(rib.point1)
        return points

    def is_included(self, address):
        if not address.get('coordinates'):
            return False
        if not address['coordinates'].get('lat') or not address['coordinates'].get('lon'):
            return False
        c = GeoPtProxy(lat=address['coordinates']['lat'], lon=address['coordinates']['lon'])
        d = GeoPtProxy(lat=90.0, lon=180)
        amount = 0
        for rib in self.geo_ribs:
            a = GeoPtProxy(lat=rib.point1.lat, lon=rib.point1.lon)
            b = GeoPtProxy(lat=rib.point2.lat, lon=rib.point2.lon)
            result = GeoPtProxy.square(a, b, c) * GeoPtProxy.square(a, b, d) < 0.0 \
                and GeoPtProxy.square(c, d, a) * GeoPtProxy.square(c, d, b) < 0.0
            if result:
                amount += 1
        logging.info('address = %s' % address)
        logging.info('in zone = %s' % (amount % 2 == 1))
        return amount % 2 == 1


class DeliveryType(ndb.Model):
    MAX_DAYS = 7
    ONE_DAY_SEC = 86400

    MODE_SLOTS = 0
    MODE_EXACT_TIME = 1
    MODE_DATE_AND_SLOTS = 2
    MODE_DUAL = 3

    delivery_type = ndb.IntegerProperty(choices=DELIVERY_TYPES)
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_UNAVAILABLE)
    min_time = ndb.IntegerProperty(default=0)
    max_time = ndb.IntegerProperty(default=ONE_DAY_SEC * MAX_DAYS)
    dual_mode = ndb.BooleanProperty(default=False)
    delivery_zones = ndb.KeyProperty(kind=DeliveryZone, repeated=True)
    delivery_slots = ndb.KeyProperty(kind=DeliverySlot, repeated=True)
    item_restrictions = ndb.KeyProperty(kind=MenuItem, repeated=True)
    category_restrictions = ndb.KeyProperty(kind=MenuCategory, repeated=True)
    schedule_restriction = ndb.LocalStructuredProperty(Schedule)
    today_schedule = ndb.LocalStructuredProperty(DaySchedule)
    default = ndb.BooleanProperty(default=False)

    @classmethod
    def create(cls, delivery_type):
        delivery = cls(id=delivery_type, delivery_type=delivery_type)
        delivery.put()
        return delivery

    def get_mode(self):
        if not self.delivery_slots:
            return self.MODE_EXACT_TIME

        slot_type = self.delivery_slots[0].get().slot_type
        if slot_type in (DeliverySlot.STRINGS, DeliverySlot.HOURS_FROM_MIDNIGHT):
            return self.MODE_DATE_AND_SLOTS

        if self.dual_mode:
            return self.MODE_DUAL
        return self.MODE_SLOTS

    def dict(self):
        mode = self.get_mode()
        return {
            'id': str(self.delivery_type),
            'name': DELIVERY_MAP[self.delivery_type],
            'time_picker_min': self.min_time,
            'time_picker_max': self.max_time,
            'slots': [slot.dict() for slot in sorted([slot.get() for slot in self.delivery_slots], key=lambda x: x.value)],
            'mode': mode,
            'time_required': mode in (self.MODE_EXACT_TIME, self.MODE_DATE_AND_SLOTS),
            'default': self.default,
        }


class Venue(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    address = ndb.StructuredProperty(Address)
    description = ndb.StringProperty(indexed=False)
    extra_info = ndb.StringProperty()
    pic = ndb.StringProperty(indexed=False)
    coordinates = ndb.GeoPtProperty(required=True, indexed=False)
    schedule = ndb.LocalStructuredProperty(Schedule)
    time_break = ndb.LocalStructuredProperty(Schedule, repeated=True)
    delivery_types = ndb.LocalStructuredProperty(DeliveryType, repeated=True)
    phones = ndb.StringProperty(repeated=True)  # use for sending sms
    emails = ndb.StringProperty(repeated=True)  # use for sending email
    problem = ndb.StringProperty(indexed=False)
    active = ndb.BooleanProperty(required=True, default=False)
    type_deliveries = ndb.IntegerProperty(repeated=True)
    timezone_offset = ndb.IntegerProperty(default=3)  # hours offset
    timezone_name = ndb.StringProperty()
    stop_lists = ndb.KeyProperty(kind=MenuItem, repeated=True)
    single_modifiers_stop_list = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_choice_modifier_stop_list = ndb.KeyProperty(kind=GroupModifierChoice, repeated=True)
    promo_restrictions = ndb.KeyProperty(kind=Promo, repeated=True)
    payment_restrictions = ndb.KeyProperty(kind=PaymentType,repeated=True)
    wallet_restriction = ndb.BooleanProperty(default=False)
    default = ndb.BooleanProperty(default=False)
    legal = ndb.KeyProperty(LegalInfo)
    called_phone = ndb.StringProperty()

    @classmethod
    def get(cls, venue_id):
        from models.config.config import config, AUTO_APP, RESTO_APP, DOUBLEB_APP
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(int(venue_id))
        elif app_kind in [RESTO_APP, DOUBLEB_APP]:
            if app_kind == DOUBLEB_APP:
                venue_id = int(venue_id)
            for venue in cls.fetch_venues(app_kind):
                if venue.key.id() == venue_id:
                    return venue

    @classmethod
    def fetch_venues(cls, *args, **kwargs):
        from models.config.config import config, AUTO_APP, RESTO_APP, DOUBLEB_APP
        from methods.proxy.resto.venues import get_venues as resto_get_venues
        from methods.proxy.doubleb.venues import get_venues as doubleb_get_venues
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            return cls.query(*args, **kwargs).fetch()
        elif app_kind in [RESTO_APP, DOUBLEB_APP]:
            if app_kind == RESTO_APP:
                venues = resto_get_venues()
            else:
                venues = doubleb_get_venues()
            for venue in venues[:]:
                for name, value in kwargs.items():
                    if getattr(venue, name) != value:
                        venues.remove(venue)
            return venues

    @classmethod
    def get_cities(cls):
        cities = []
        for venue in cls.query(cls.active == True).fetch():
            if venue.address.city not in cities:
                cities.append(venue.address.city)
        return cities

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
            'company_namespace': self.key.namespace(),
            'distance': distance,
            'title': self.title,
            'address': self.description,
            'pic': self.pic,
            'lat': self.coordinates.lat,
            'lon': self.coordinates.lon,
            'coordinates': str(self.coordinates),
            'is_open': self.is_open(),
            'deliveries': [delivery.dict() for delivery in self.delivery_types if delivery.status == STATUS_AVAILABLE],
            'schedule': self.schedule.dict() if self.schedule else [],
            'schedule_str': self.schedule.get_days_str() if self.schedule else '',
            'time_breaks': [time_break.dict() for time_break in self.time_break],
            'time_breaks_str': [time_break.get_days_str() for time_break in self.time_break],
            'called_phone': self.called_phone,
            'extra_info': self.extra_info,
            'text_color': 'FFFFFF',  # for unified app
        }
        return dct

    def admin_dict(self):
        return {
            'id': self.key.id(),
            'title': self.title,
            'address': self.description
        }

    @classmethod
    def get_suitable_venues(cls, city):
        return [venue for venue in cls.query(cls.address.city == city.city).fetch() if venue.active]

    def suitable_for_city(self, city):
        return self.address.city == city.city

    def is_open(self, minutes_offset=0):
        now = datetime.utcnow() + timedelta(minutes=minutes_offset) + timedelta(hours=self.timezone_offset)
        return working_hours.check(self.schedule, now)

    def update_address(self):
        from models.config.config import Config
        from methods import geocoder

        candidates = geocoder.get_houses_by_coordinates(self.coordinates.lat, self.coordinates.lon)
        if candidates:
            address = candidates[0]
            self.address = Address(**address['address'])
            cfg = Config.get()
            if self.address.country not in cfg.COUNTRIES:
                cfg.COUNTRIES.append(self.address.country)
                cfg.put()
        self.update_timezone()

    def update_timezone(self):
        from methods import timezone
        zone = timezone.get_time_zone(self.coordinates.lat, self.coordinates.lon)
        if zone:
            self.timezone_offset = zone['offset']
            self.timezone_name = zone['name']

    @classmethod
    def get_first_tz(cls):
        venue = cls.query().fetch()
        return venue.timezone_offset()
