# coding=utf-8
import threading
from google.appengine.api import memcache
from google.appengine.ext import ndb

VENUE = 0
BAR = 1

PLACE_TYPES = [
    VENUE, BAR
]


class Config(ndb.Model):
    CANCEL_ALLOWED_WITHIN = ndb.IntegerProperty(indexed=False, default=30)  # seconds after creation
    CANCEL_ALLOWED_BEFORE = ndb.IntegerProperty(indexed=False, default=3)  # minutes before delivery_time

    CARD_BINDING_REQUIRED = True
    
    ALFA_BASE_URL = ndb.StringProperty(indexed=False, default="https://test.paymentgate.ru/testpayment")
    ALFA_LOGIN = ndb.StringProperty(indexed=False, default="empatika_autopay-api")
    ALFA_PASSWORD = ndb.StringProperty(indexed=False, default="empatika_autopay")

    PROMOS_API_KEY = ndb.StringProperty(indexed=False)

    PLACE_TYPE = ndb.IntegerProperty(choices=PLACE_TYPES)

    WALLET_API_KEY = ndb.StringProperty(indexed=False)
    WALLET_MAX_PERCENT = ndb.IntegerProperty(default=100)

    EMAILS = ndb.JsonProperty(default={
        "server": "admins",
    })

    IN_PRODUCTION = ndb.BooleanProperty(indexed=False, default=True)

    APP_NAME = ndb.StringProperty(indexed=False)
    COMPANY_NAME = ndb.StringProperty(indexed=False)
    COMPANY_DESCRIPTION = ndb.StringProperty(indexed=False)  # suitable name is APP_DESCRIPTION
    COMPANY_ADDRESS = ndb.StringProperty(indexed=False)
    SUPPORT_PHONE = ndb.StringProperty(indexed=False)
    SUPPORT_SITE = ndb.StringProperty(indexed=False)
    SUPPORT_EMAILS = ndb.StringProperty(indexed=False, repeated=True)
    DELIVERY_PHONE = ndb.StringProperty(indexed=False)
    DELIVERY_EMAILS = ndb.StringProperty(indexed=False, repeated=True)

    LEGAL_PERSON = ndb.StringProperty(indexed=False)     # OOO
    LEGAL_PERSON_IP = ndb.StringProperty(indexed=False)  # IP
    LEGAL_CONTACTS = ndb.StringProperty(indexed=False)
    LEGAL_EMAIL = ndb.StringProperty(indexed=False)
    INN = ndb.StringProperty(indexed=False)
    KPP = ndb.StringProperty(indexed=False)
    OGRN = ndb.StringProperty(indexed=False)
    OGRNIP = ndb.StringProperty(indexed=False)

    COUNTRIES = ndb.StringProperty(indexed=False, repeated=True)

    def get_place_str(self):
        if self.PLACE_TYPE == VENUE:
            return u'Кофейня'
        elif self.PLACE_TYPE == BAR:
            return u'Бар'

    @property
    def WALLET_ENABLED(self):
        return self.WALLET_API_KEY is not None

    @classmethod
    def GET_MAX_WALLET_SUM(cls, total_sum):
        config = cls.get()
        return total_sum * config.WALLET_MAX_PERCENT / 100.0

    PAYPAL_CLIENT_ID = ndb.StringProperty(indexed=False)
    PAYPAL_CLIENT_SECRET = ndb.StringProperty(indexed=False)
    PAYPAL_SANDBOX = ndb.BooleanProperty(indexed=False, required=True, default=True)

    @property
    def PAYPAL_API(self):
        api = memcache.get('paypal_api')
        if not api:
            from methods import paypalrestsdk
            mode = "sandbox" if self.PAYPAL_SANDBOX else "live"
            api = paypalrestsdk.Api(mode=mode, client_id=self.PAYPAL_CLIENT_ID, client_secret=self.PAYPAL_CLIENT_SECRET)
            memcache.set('paypal_api', api)
        return api

    @classmethod
    def get(cls):
        config = cls.get_by_id(1)
        if not config:
            config = Config(id=1)
            config.put()
        return config


class LocalConfigProxy(object):
    _local = threading.local()

    @property
    def _config_object(self):
        try:
            self._local.config
        except AttributeError:
            self._local.config = Config.get()
        return self._local.config

    def __getattr__(self, item):
        return getattr(self._config_object, item)


config = LocalConfigProxy()
