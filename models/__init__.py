from google.appengine.ext import ndb

__author__ = 'ilyazorin'

CASH_PAYMENT_TYPE = 0
CARD_PAYMENT_TYPE = 1

STATUS_AVAILABLE = 1
STATUS_UNAVAILABLE = 0

NEW_ORDER = 0
READY_ORDER = 1
CANCELED_BY_CLIENT_ORDER = 2
CANCELED_BY_BARISTA_ORDER = 3

#TODO not sure
PAYMENT_SUCCESS = 1
PAYMENT_FAIL = 0

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

class MenuCategory(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    picture = ndb.StringProperty(indexed=False)
    menu_items = ndb.KeyProperty(kind=MenuItem, repeated=True, indexed=False)

class Venue(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    description = ndb.StringProperty(indexed=False)
    pic = ndb.StringProperty(indexed=False)
    coordinates = ndb.GeoPtProperty(required=True, indexed=False)
    working_days = ndb.StringProperty(indexed=False)
    working_hours = ndb.StringProperty(indexed=False)
    menu = ndb.KeyProperty(kind=MenuCategory, repeated=True, indexed=False)
    phone_numbers = ndb.StringProperty(repeated=True, indexed=False)

    def dict(self):
        dct = {
            'id': self.key.id(),
            'distance': 0,
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
    delivery_time = ndb.TimeProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=(CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE))
    payment_status = ndb.IntegerProperty(choices=(PAYMENT_SUCCESS, PAYMENT_FAIL))
    coordinates = ndb.GeoPtProperty(indexed=False)
    venue_id = ndb.IntegerProperty(required=True)
    pan = ndb.StringProperty(indexed=False)
    return_comment = ndb.StringProperty(indexed=False)
    comment = ndb.StringProperty(indexed=False)
    return_datetime = ndb.DateTimeProperty(indexed=False)
    payment_id = ndb.StringProperty()
    device_type = ndb.IntegerProperty(required=True)

class Client(ndb.Model):
    name = ndb.StringProperty(required=True, indexed=False)
    tel = ndb.StringProperty(required=True, indexed=False)

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
