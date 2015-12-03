from datetime import date
import logging

from google.appengine.api import namespace_manager
from google.appengine.ext import ndb, deferred
from methods import fastcounter
from models import STATUS_AVAILABLE
from models.config.version import CURRENT_APP_ID, PRODUCTION_APP_ID
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
    has_phone = ndb.BooleanProperty(default=False, indexed=False)
    
    @classmethod
    def save(cls, client_namespace, client_id, date, order_screen, non_empty_cart, has_phone):
        key_name = "%s%s%s" % (date.strftime(cls._DATE_FMT_STR), cls._DATE_ID_SEPARATOR, client_id)
        key = ndb.Key(cls, key_name, namespace=client_namespace)
        sess = key.get()
        put = False
        if not sess:
            sess = cls(key=key)
            put = True
        if order_screen and not sess.order_screen:
            sess.order_screen = True
            put = True
        if non_empty_cart and not sess.non_empty_cart:
            sess.non_empty_cart = True
            put = True
        if has_phone and not sess.has_phone:
            sess.has_phone = True
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
    MIN_GLOBAL_ID = 10000

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
    namespace_created = ndb.StringProperty()
    extra_data = ndb.JsonProperty()
    paypal_refresh_token = ndb.StringProperty(indexed=False)
    city = ndb.KeyProperty(kind=ProxyCity)

    @classmethod
    def create(cls, client_id=None):
        ns = namespace_manager.get_namespace()
        namespace_manager.set_namespace('')
        if not client_id:
            client_id = cls.generate_id()
        client = cls(id=client_id, namespace_created=ns)
        namespace_manager.set_namespace(ns)
        return client

    @staticmethod
    def generate_id():
        value = fastcounter.get_count("client_id")
        fastcounter.incr("client_id")
        return value + 1

    def save_session(self, order_screen=False, non_empty_cart=False):
        try:
            deferred.defer(ClientSession.save,
                           self.key.namespace() or self.namespace_created, self.key.id(), date.today(),
                           order_screen, non_empty_cart, bool(self.tel))
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

    @classmethod
    def is_id_global(cls, client_id):
        if CURRENT_APP_ID == PRODUCTION_APP_ID:
            return client_id >= cls.MIN_GLOBAL_ID
        return True

    @classmethod
    def get(cls, client_id):
        kwds = {}
        if cls.is_id_global(client_id):
            kwds['namespace'] = ''
        return cls.get_by_id(client_id, **kwds)

    @classmethod
    def find_by_android_id(cls, android_id):
        client = cls.query(cls.android_id == android_id).get()
        if not client:
            client = cls.query(cls.android_id == android_id,
                               cls.namespace_created == namespace_manager.get_namespace(),
                               namespace='').get()
        return client


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