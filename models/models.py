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

#TODO no sure
PAYMENT_SUCCESS = 1
PAYMENT_FAIL = 0

IOS_DEVICE = 0
ANDROID_DEVICE = 1

class Venue(ndb.Model):
    venue_id = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    pic = ndb.StringProperty()
    coordinates = ndb.GeoPtProperty(required=True)
    #TODO better solution than string?
    working_days = ndb.StringProperty()
    working_hours = ndb.StringProperty()
    menu = ndb.KeyProperty(kind=MenuCategory, repeated=True)

class Client(ndb.Model):
    client_id = ndb.IntegerProperty(required=True)
    name = ndb.StringProperty(required=True)
    tel = ndb.StringProperty(required=True)

class MenuCategory(ndb.Model):
    category_id = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(required=True)
    picture = ndb.StringProperty()
    menu_items = ndb.KeyProperty(kind=MenuItem, repeated=True)

class MenuItem(ndb.Model):
    menu_item_id = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    picture = ndb.StringProperty()
    kal = ndb.IntegerProperty()
    price = ndb.IntegerProperty(required=True)
    cost_price = ndb.IntegerProperty()
    status = ndb.IntegerProperty(required=True, choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE),
                                 default=STATUS_AVAILABLE)

class PaymentType(ndb.Model):
    payment_id = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty()
    status = ndb.IntegerProperty(required=True, choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE),
                                 default=STATUS_AVAILABLE)

class Order(ndb.Model):
    order_id = ndb.IntegerProperty(required=True)
    client_id = ndb.IntegerProperty(required=True)
    #TODO can be calculated from menu items or nevermind?
    total_sum = ndb.IntegerProperty()
    status = ndb.IntegerProperty(required=True, choices=(NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER,
                                                         CANCELED_BY_BARISTA_ORDER),
                                 default=NEW_ORDER)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    delivery_time = ndb.TimeProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=(CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE))
    payment_status = ndb.IntegerProperty(choices=(PAYMENT_SUCCESS, PAYMENT_FAIL))
    coordinates = ndb.GeoPtProperty()
    venue_id = ndb.IntegerProperty(required=True)
    pan = ndb.StringProperty()
    #TODO whats the difference?
    return_comment = ndb.StringProperty()
    comment = ndb.StringProperty()
    return_datetime = ndb.DateTimeProperty()
    #TODO alpha order id maybe?
    payment_id = ndb.StringProperty()
    device_type = ndb.IntegerProperty(required=True)






