from datetime import date
import logging
from google.appengine.ext import ndb, deferred
from methods import fastcounter
from models import STATUS_AVAILABLE
from models.proxy.unified_app import ProxyCity

IOS_DEVICE = 0
ANDROID_DEVICE = 1
WEB_DEVICE = 2
DEVICE_CHOICES = (IOS_DEVICE, ANDROID_DEVICE, WEB_DEVICE)
DEVICE_TYPE_MAP = {
    IOS_DEVICE: 'ios',
    ANDROID_DEVICE: 'android'
}


class ClientSession(ndb.Model):
    _DATE_FMT_STR = "%Y-%m-%d"
    _DATE_ID_SEPARATOR = "|"
    _SEPARATOR_NEXT_CHAR = chr(ord(_DATE_ID_SEPARATOR) + 1)

    order_screen = ndb.BooleanProperty(default=False, indexed=False)
    non_empty_cart = ndb.BooleanProperty(default=False, indexed=False)
    
    @classmethod
    def save(cls, client_id, date, order_screen, non_empty_cart):
        key_name = "%s%s%s" % (date.strftime(cls._DATE_FMT_STR), cls._DATE_ID_SEPARATOR, client_id)
        sess = cls.get_by_id(key_name)
        put = False
        if not sess:
            sess = cls(id=key_name)
            put = True
        if order_screen and not sess.order_screen:
            sess.order_screen = True
            put = True
        if non_empty_cart and not sess.non_empty_cart:
            sess.non_empty_cart = True
            put = True
        if put:
            sess.put()

    @classmethod
    def query_by_date(cls, date):
        date_str = date.strftime("%Y-%m-%d")
        min_key = ndb.Key(cls, date_str + cls._DATE_ID_SEPARATOR)
        max_key = ndb.Key(cls, date_str + cls._SEPARATOR_NEXT_CHAR)
        return cls.query(cls.key >= min_key, cls.key < max_key)

    @property
    def date(self):
        date_str, _ = self.key.id().split(self._DATE_ID_SEPARATOR)
        return date.strptime(self._DATE_FMT_STR)

    @property
    def client_id(self):
        _, client_id = self.key.id().split(self._DATE_ID_SEPARATOR)
        return client_id


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
    paypal_refresh_token = ndb.StringProperty(indexed=False)
    city = ndb.KeyProperty(kind=ProxyCity)
    extra_data = ndb.JsonProperty()

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

    def save_session(self, order_screen=False, non_empty_cart=False):
        try:
            deferred.defer(ClientSession.save, self.key.id(), date.today(), order_screen, non_empty_cart)
        except Exception as e:
            logging.error("failed to defer save_session()")
            logging.exception(e)

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