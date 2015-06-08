from google.appengine.ext import ndb
from methods import fastcounter

IOS_DEVICE = 0
ANDROID_DEVICE = 1

DEVICE_TYPE_MAP = {
    IOS_DEVICE: 'ios',
    ANDROID_DEVICE: 'android'
}


class Client(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    user_agent = ndb.StringProperty(indexed=False)
    tied_card = ndb.BooleanProperty(default=False)
    device_phone = ndb.StringProperty()
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    tel = ndb.StringProperty()
    email = ndb.StringProperty()

    name_confirmed = ndb.BooleanProperty(default=False)
    name_for_sms = ndb.StringProperty(default='')

    paypal_refresh_token = ndb.StringProperty(indexed=False)

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
            "id": self.key.id(),
            "name": self.name,
            "surname": self.surname,
            "phone": self.tel
        }


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