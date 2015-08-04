# coding=utf-8
import threading
from google.appengine.api import memcache
from google.appengine.ext import ndb

OTHER = -1
VENUE = 0
BAR = 1
PLACE_TYPES = (OTHER, VENUE, BAR)

COFFEE_LOGIC = 0
MEAL_LOGIC = 1
OTHER = 2
SCREEN_LOGICS = (COFFEE_LOGIC, MEAL_LOGIC, OTHER)

DEMO_HOSTNAME = u'automation-demo.appspot.com'
PRODUCTION_HOSTNAME = u'doubleb-automation-production.appspot.com'
TEST_VERSIONS = ('.test2.', '.p-test.', '.courier.')

EMAIL_FROM = 'noreply-order@ru-beacon.ru'


class Config(ndb.Model):
    CANCEL_ALLOWED_WITHIN = ndb.IntegerProperty(indexed=False, default=30)  # seconds after creation
    CANCEL_ALLOWED_BEFORE = ndb.IntegerProperty(indexed=False, default=3)  # minutes before delivery_time
    
    ALFA_BASE_URL = ndb.StringProperty(indexed=False, default="https://test.paymentgate.ru/testpayment")
    ALFA_LOGIN = ndb.StringProperty(indexed=False, default="empatika_autopay-api")
    ALFA_PASSWORD = ndb.StringProperty(indexed=False, default="empatika_autopay")

    PARSE_APP_API_KEY = ndb.StringProperty(indexed=False)   # todo: rewrite pushes, delete field
    PARSE_REST_API_KEY = ndb.StringProperty(indexed=False)  # todo: rewrite pushes, delete field

    EMAIL_REQUESTS = ndb.BooleanProperty(default=False)

    PROMOS_API_KEY = ndb.StringProperty(indexed=False)

    PLACE_TYPE = ndb.IntegerProperty(choices=PLACE_TYPES, default=OTHER)
    SCREEN_LOGIC = ndb.IntegerProperty(choices=SCREEN_LOGICS, default=OTHER)

    WALLET_API_KEY = ndb.StringProperty(indexed=False)
    WALLET_MAX_PERCENT = ndb.IntegerProperty(default=100)

    SEND_ERRORS_500 = ndb.BooleanProperty(indexed=False, default=False)

    SHARED_INVITATION_SENDER_ACCUMULATED_POINTS = ndb.IntegerProperty(indexed=False, default=0)
    SHARED_INVITATION_SENDER_WALLET_POINTS = ndb.IntegerProperty(indexed=False, default=0)
    SHARED_INVITATION_RECIPIENT_ACCUMULATED_POINTS = ndb.IntegerProperty(indexed=False, default=0)
    SHARED_INVITATION_RECIPIENT_WALLET_POINTS = ndb.IntegerProperty(indexed=False, default=0)

    BRANCH_API_KEY = ndb.StringProperty(indexed=False)

    APP_NAME = ndb.StringProperty(indexed=False)
    COMPANY_DESCRIPTION = ndb.StringProperty(indexed=False)  # suitable name is APP_DESCRIPTION
    SUPPORT_PHONE = ndb.StringProperty(indexed=False)
    SUPPORT_SITE = ndb.StringProperty(indexed=False)
    SUPPORT_EMAILS = ndb.StringProperty(indexed=False, repeated=True)
    ADDITION_INFO_ABOUT_DELIVERY = ndb.StringProperty(indexed=False)

    COUNTRIES = ndb.StringProperty(indexed=False, repeated=True)
    COMPULSORY_ADDRESS_VALIDATES = ndb.BooleanProperty(indexed=False, default=False)

    REPORT_EMAILS = ndb.StringProperty(indexed=False)

    EXTRA_CLIENT_INFO_FIELDS = ndb.StringProperty(indexed=False, repeated=True)

    ACTION_COLOR = ndb.StringProperty(indexed=False, default='FF000000')

    def get_place_str(self):
        if self.PLACE_TYPE == VENUE:
            return u'Кофейня'
        elif self.PLACE_TYPE == BAR:
            return u'Бар'

    @property
    def WALLET_ENABLED(self):
        return self.WALLET_API_KEY is not None

    @classmethod
    def GET_MAX_WALLET_SUM(cls, total_sum):  # must be positive
        config = cls.get()
        return total_sum * config.WALLET_MAX_PERCENT / 100.0

    @property
    def GIFT_ENABLED(self):
        return self.PROMOS_API_KEY is not None

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