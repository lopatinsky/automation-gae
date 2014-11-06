from collections import Counter
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth import models
from methods import location, fastcounter
from methods.rendering import timestamp

__author__ = 'ilyazorin'

CASH_PAYMENT_TYPE = 0
CARD_PAYMENT_TYPE = 1
BONUS_PAYMENT_TYPE = 2

STATUS_AVAILABLE = 1
STATUS_UNAVAILABLE = 0

NEW_ORDER = 0
READY_ORDER = 1
CANCELED_BY_CLIENT_ORDER = 2
CANCELED_BY_BARISTA_ORDER = 3

IOS_DEVICE = 0
ANDROID_DEVICE = 1


class MenuItem(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    description = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=False)
    kal = ndb.IntegerProperty(indexed=False)
    price = ndb.IntegerProperty(required=True, indexed=False)
    cost_price = ndb.IntegerProperty(indexed=False)
    status = ndb.IntegerProperty(required=True, choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE),
                                 default=STATUS_AVAILABLE)

    def dict(self):
        dct = {
            'id': str(self.key.id()),
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'kal': self.kal,
            'pic': self.picture
        }
        return dct


class MenuCategory(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    picture = ndb.StringProperty(indexed=False)
    menu_items = ndb.KeyProperty(kind=MenuItem, repeated=True, indexed=False)

    def dict(self):
        return {self.title: [menu_item.get().dict() for menu_item in self.menu_items
                             if menu_item.get().status == STATUS_AVAILABLE]}


class Venue(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    description = ndb.StringProperty(indexed=False)
    pic = ndb.StringProperty(indexed=False)
    coordinates = ndb.GeoPtProperty(required=True, indexed=False)
    working_days = ndb.StringProperty(indexed=False)
    working_hours = ndb.StringProperty(indexed=False)
    menu = ndb.KeyProperty(kind=MenuCategory, repeated=True, indexed=False)
    phone_numbers = ndb.StringProperty(repeated=True, indexed=False)

    def dict(self, user_location=None):
        distance = 0
        if user_location:
            distance = location.distance(ndb.GeoPt(user_location), self.coordinates)
        dct = {
            'id': str(self.key.id()),
            'distance': distance,
            'title': self.title,
            'address': self.description,
            'pic': self.pic,
            'lat': self.coordinates.lat,
            'lon': self.coordinates.lon,
            'coordinates': str(self.coordinates),
            'schedule': []
        }
        working_days = self.working_days.split(',')
        working_hours = self.working_hours.split(',')
        for i in xrange(len(working_days)):
            dct['schedule'].append({'days': [int(day) for day in working_days[i]],
                                    'hours': working_hours[i]})
        return dct


class Order(ndb.Model):
    client_id = ndb.IntegerProperty(required=True)
    total_sum = ndb.IntegerProperty(indexed=False)
    status = ndb.IntegerProperty(required=True, choices=(NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER,
                                                         CANCELED_BY_BARISTA_ORDER),
                                 default=NEW_ORDER)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    delivery_time = ndb.DateTimeProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=(CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE,
                                                                  BONUS_PAYMENT_TYPE))
    coordinates = ndb.GeoPtProperty(indexed=False)
    venue_id = ndb.IntegerProperty(required=True)
    pan = ndb.StringProperty(indexed=False)
    return_comment = ndb.StringProperty(indexed=False)
    comment = ndb.StringProperty(indexed=False)
    return_datetime = ndb.DateTimeProperty()
    payment_id = ndb.StringProperty()
    device_type = ndb.IntegerProperty(required=True)
    items = ndb.KeyProperty(indexed=False, repeated=True, kind=MenuItem)
    mastercard = ndb.BooleanProperty(indexed=False)

    def dict(self):
        dct = {
            "order_id": self.key.id(),
            "delivery_time": timestamp(self.delivery_time),
            "payment_type_id": self.payment_type_id,
            "client": Client.get_by_id(self.client_id).dict(),
            "pan": self.pan,
            "comment": self.comment,
            "items": []
        }
        for item_key, count in Counter(self.items).items():
            item = item_key.get()
            dct["items"].append({
                "title": item.title,
                "price": item.price,
                "quantity": count
            })
        return dct

    def status_dict(self):
        dct = {
            'order_id': str(self.key.id()),
            'status': self.status
        }

        return dct

    @staticmethod
    def generate_id():
        value = fastcounter.get_count("order_id")
        fastcounter.incr("order_id")
        return value + 1


class Client(ndb.Model):
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    tel = ndb.StringProperty()
    has_mastercard_orders = ndb.BooleanProperty(default=False, indexed=False)

    @classmethod
    def create(cls):
        return cls(id=cls.generate_id())

    @staticmethod
    def generate_id():
        value = fastcounter.get_count("client_id")
        fastcounter.incr("client_id")
        return value + 1

    def dict(self):
        return {
            "name": self.name,
            "surname": self.surname,
            "phone": self.tel
        }


class PaymentType(ndb.Model):
    title = ndb.StringProperty(indexed=False)
    status = ndb.IntegerProperty(required=True, choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE),
                                 default=STATUS_AVAILABLE)

    def dict(self):
        dct = {
            'id': int(self.key.id()),
            'title': self.title
        }

        return dct


class News(ndb.Model):
    text = ndb.StringProperty(required=True, indexed=False)
    image_url = ndb.StringProperty(required=True, indexed=False)
    active = ndb.BooleanProperty(required=True, default=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    def dict(self):
        return {
            "id": self.key.id(),
            "text": self.text,
            "image_url": self.image_url,
            "created_at": timestamp(self.created_at)
        }


class Admin(models.User):
    email = ndb.StringProperty(required=True, indexed=False)
    venue = ndb.KeyProperty(Venue, indexed=False)  # None for global admin, actual venue for barista

    def query_orders(self, *args, **kwargs):
        if self.venue:
            return Order.query(Order.venue_id == self.venue.id(), *args, **kwargs)
        return Order.query(*args, **kwargs)

    def order_by_id(self, order_id):
        order = Order.get_by_id(order_id)
        if not order:
            return None
        if self.venue and order.venue_id != self.venue.id():
            return None
        return order


class AdminStatus(ndb.Model):
    location = ndb.GeoPtProperty()
    time = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def _make_key_name(uid, token):
        return "%s_%s" % (uid, token)

    @classmethod
    def create(cls, uid, token, location):
        key_name = cls._make_key_name(uid, token)
        entity = cls(id=key_name, location=location)
        entity.put()
        return entity

    @classmethod
    def get(cls, uid, token):
        key_name = cls._make_key_name(uid, token)
        return cls.get_by_id(key_name)

    @property
    def admin(self):
        uid = int(self.key.id().split("_")[0])
        return Admin.get_by_id(uid)
