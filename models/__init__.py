from collections import Counter
import datetime
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth import models
from methods import location, fastcounter, working_hours
from methods.rendering import timestamp, opt
from tablet_request import TabletRequest
from error_statistics import PaymentErrorsStatistics, AlfaBankRequest
from config import config
from methods.empatika_promos import register_order

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
CREATING_ORDER = 4

IOS_DEVICE = 0
ANDROID_DEVICE = 1

PUSH_NOTIFICATION = 0
SMS_SUCCESS = 1
SMS_PASSIVE = 2


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
    status = ndb.IntegerProperty(choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE), default=STATUS_AVAILABLE)

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
    holiday_schedule = ndb.StringProperty(indexed=False)
    problem = ndb.StringProperty(indexed=False)
    takeout_only = ndb.BooleanProperty(indexed=False, default=False)
    active = ndb.BooleanProperty(required=True, default=False)

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

    def is_open(self, minutes_offset=0):
        now = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes_offset)
        return working_hours.check(self.working_days, self.working_hours, now, self.holiday_schedule)


class OrderPositionDetails(ndb.Model):
    item = ndb.KeyProperty(MenuItem, required=True)
    price = ndb.IntegerProperty(required=True)
    revenue = ndb.IntegerProperty(required=True)
    promos = ndb.StringProperty(repeated=True)


class Order(ndb.Model):
    client_id = ndb.IntegerProperty(required=True)
    total_sum = ndb.IntegerProperty(indexed=False)
    status = ndb.IntegerProperty(required=True, choices=(NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER,
                                                         CANCELED_BY_BARISTA_ORDER, CREATING_ORDER),
                                 default=CREATING_ORDER)
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
    item_details = ndb.LocalStructuredProperty(OrderPositionDetails, repeated=True)
    promos = ndb.StringProperty(repeated=True, indexed=False)
    mastercard = ndb.BooleanProperty(indexed=True)
    actual_delivery_time = ndb.DateTimeProperty(indexed=False)
    response_success = ndb.BooleanProperty(default=False, indexed=False)

    first_for_client = ndb.BooleanProperty()

    def dict(self):
        dct = {
            "order_id": self.key.id(),
            "venue": Venue.get_by_id(self.venue_id).admin_dict(),
            "status": self.status,
            "delivery_time": timestamp(self.delivery_time),
            "actual_delivery_time": opt(timestamp, self.actual_delivery_time),
            "payment_type_id": self.payment_type_id,
            "client": Client.get_by_id(self.client_id).dict(),
            "pan": self.pan,
            "comment": self.comment,
            "return_comment": self.return_comment,
            "items": []
        }
        items_str = []
        for item_detail in self.item_details:
            items_str.append('%s_%s' % (item_detail.item.get().title, item_detail.price))
        for item_str, count in Counter(items_str).items():
            dct["items"].append({
                "title": item_str.split('_')[0],
                "price": item_str.split('_')[1],
                "quantity": count
            })
        return dct

    def status_dict(self):
        dct = {
            'order_id': str(self.key.id()),
            'status': self.status
        }

        return dct

    def history_dict(self):
        dct = {
            "order_id": self.key.id(),
            "status": self.status,
            "delivery_time": timestamp(self.delivery_time),
            "payment_type_id": self.payment_type_id,
            "total": self.total_sum,
            "venue_id": self.venue_id,
            "items": []
        }

        for item_key, count in Counter(self.items).items():
            item = item_key.get()
            dct["items"].append({
                "id": item_key.id(),
                "title": item.title,
                "price": item.price,
                "quantity": count
            })
        return dct

    @staticmethod
    def generate_id():
        value = fastcounter.get_count("order_id")
        fastcounter.incr("order_id")
        return value + 1


class Notification(ndb.Model):
    client_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    type = ndb.IntegerProperty(required=True, choices=(PUSH_NOTIFICATION, SMS_SUCCESS, SMS_PASSIVE))


class Client(ndb.Model):
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    tel = ndb.StringProperty()
    email = ndb.StringProperty()
    has_mastercard_orders = ndb.BooleanProperty(default=False, indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

    name_confirmed = ndb.BooleanProperty(default=False)

    user_agent = ndb.StringProperty(indexed=False)
    tied_card = ndb.BooleanProperty(default=False)
    device_phone = ndb.StringProperty()

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

    PADMIN = 'padmin'

    email = ndb.StringProperty(required=True, indexed=False)
    venue = ndb.KeyProperty(Venue, indexed=True)  # None for global admin, actual venue for barista

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

    @property
    def login(self):
        return self.email

    def delete_auth_ids(self):
        class_name = type(self).__name__
        ids = ["%s.auth_id:%s" % (class_name, i) for i in self.auth_ids]
        self.unique_model.delete_multi(ids)


class AdminStatus(ndb.Model):
    location = ndb.GeoPtProperty()
    time = ndb.DateTimeProperty(auto_now=True)
    readonly = ndb.BooleanProperty(default=False)

    @staticmethod
    def _make_key_name(uid, token):
        return "%s_%s" % (uid, token)

    @classmethod
    def create(cls, uid, token, location, readonly):
        key_name = cls._make_key_name(uid, token)
        entity = cls(id=key_name, location=location, readonly=readonly)
        entity.put()
        return entity

    @classmethod
    def get(cls, uid, token):
        key_name = cls._make_key_name(uid, token)
        return cls.get_by_id(key_name)

    @property
    def admin_id(self):
        return int(self.key.id().split("_")[0])

    @property
    def admin(self):
        return Admin.get_by_id(self.admin_id)

    @property
    def token(self):
        return self.key.id().split("_")[1]


class JsonStorage(ndb.Model):
    data = ndb.JsonProperty()

    @classmethod
    def get(cls, storage_id):
        entity = cls.get_by_id(storage_id)
        if entity:
            return entity.data
        return None

    @classmethod
    def save(cls, storage_id, data):
        if data is None:
            cls.delete(storage_id)
        else:
            cls(id=storage_id, data=data).put()

    @classmethod
    def delete(cls, storage_id):
        ndb.Key(cls, storage_id).delete()


class CardBindingPayment(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    client_id = ndb.IntegerProperty()
    success = ndb.BooleanProperty()  # None if status unknown
    error = ndb.IntegerProperty()  # None if error unknown
    error_description = ndb.StringProperty()

    @property
    def order_id(self):
        return self.key.id()


class Share(ndb.Model):
    from methods.branch_io import SHARE, INVITATION, GIFT

    ACTIVE = 0
    INACTIVE = 1

    sender = ndb.KeyProperty(required=True, kind=Client)
    share_type = ndb.IntegerProperty(required=True, choices=[SHARE, INVITATION, GIFT])
    status = ndb.IntegerProperty(default=ACTIVE)
    url = ndb.StringProperty()

    def deactivate(self):
        self.status = self.INACTIVE
        self.put()


class SharedFreeCup(ndb.Model):  # free cup is avail after recipient orders smth and should be deleted after that
    ACTIVE = 0
    INACTIVE = 1

    sender = ndb.KeyProperty(required=True, kind=Client)
    recipient = ndb.KeyProperty(required=True, kind=Client)
    status = ndb.IntegerProperty(choices=[ACTIVE, INACTIVE], default=INACTIVE)
    order_id = ndb.IntegerProperty()

    def activate_cup(self):
        order_id = Order.generate_id()  # TODO: Миша, is it valid?
        register_order(user_id=self.sender.id(), points=config.POINTS_PER_CUP, order_id=order_id)
        self.order_id = order_id
        self.status = self.ACTIVE
        self.put()


class SharedGift(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    share_id = ndb.IntegerProperty(required=True)
    client_id = ndb.IntegerProperty(required=True)  # Who pays for cup
    total_sum = ndb.IntegerProperty(required=True)
    order_id = ndb.IntegerProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=(CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE,
                                                                  BONUS_PAYMENT_TYPE))
    payment_id = ndb.StringProperty(required=True)

    def activate_cup(self, client):
        register_order(user_id=client.key.id(), points=config.POINTS_PER_CUP,
                       order_id=self.order_id)
        self.status = Share.INACTIVE
        self.put()