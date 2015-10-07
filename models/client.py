from google.appengine.ext import ndb
from methods import fastcounter
from models import STATUS_AVAILABLE

IOS_DEVICE = 0
ANDROID_DEVICE = 1
DEVICE_CHOICES = (IOS_DEVICE, ANDROID_DEVICE)
DEVICE_TYPE_MAP = {
    IOS_DEVICE: 'ios',
    ANDROID_DEVICE: 'android'
}


class Client(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    user_agent = ndb.StringProperty(indexed=False)
    device_type = ndb.IntegerProperty(choices=DEVICE_CHOICES)
    tied_card = ndb.BooleanProperty(default=False)
    android_id = ndb.StringProperty()
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    tel = ndb.StringProperty()
    email = ndb.StringProperty()

    extra_data = ndb.JsonProperty()

    paypal_refresh_token = ndb.StringProperty(indexed=False)

    @classmethod
    def create(cls, client_id=None):
        if not client_id:
            client_id = cls.generate_id()
        return cls(id=client_id)

    @staticmethod
    def generate_id():
        value = fastcounter.get_count("client_id")
        fastcounter.incr("client_id")
        return value + 1

    def dict(self, with_extra_fields=False):
        dct = {
            "id": self.key.id(),
            "name": self.name,
            "surname": self.surname,
            "phone": self.tel
        }
        if with_extra_fields:
            from models.config.config import config
            from methods.rendering import latinize
            extra = []
            if config.CLIENT_MODULE and config.CLIENT_MODULE.status == STATUS_AVAILABLE:
                for field in config.CLIENT_MODULE.extra_fields:
                    key = latinize(field.title)
                    value = self.extra_data and self.extra_data.get(key)
                    extra.append({
                        "field": key,
                        "title": field.title,
                        "value": value
                    })
            dct["extra_data"] = extra
        return dct


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