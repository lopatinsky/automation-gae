# coding=utf-8
SUBSCRIPTION = 0
SHARE_GIFT = 1
SHARE_INVITATION = 2
ORDER_INFO_MODULE = 3
CLIENT_INFO_MODULE = 4
GEO_PUSH_MODULE = 5
MODULE_TYPES = (SUBSCRIPTION, SHARE_GIFT, SHARE_INVITATION, ORDER_INFO_MODULE, CLIENT_INFO_MODULE)

from google.appengine.api import memcache
from google.appengine.ext import ndb
from webapp2 import cached_property
from models.config.local import LocalConfigProxy
from models.config.share import ShareInvitationModule, ShareGiftModule
from models.config.field import ClientModule, OrderModule
from models.config.subscription import SubscriptionModule
from models.config.version import Version
from models.config.geo_push import GeoPushModule
from models.config.inactive_clients import SendingSmsModule

OTHER = -1
VENUE = 0
BAR = 1
PLACE_TYPES = (OTHER, VENUE, BAR)

COFFEE_LOGIC = 0
MEAL_LOGIC = 1
OTHER = 2
SCREEN_LOGICS = (COFFEE_LOGIC, MEAL_LOGIC, OTHER)

EMAIL_FROM = 'noreply-order@ru-beacon.ru'

AUTO_APP = 0
RESTO_APP = 1
APP_CHOICES = (AUTO_APP, RESTO_APP)


class Config(ndb.Model):
    @cached_property
    def APP_KIND(self):
        from models.proxy.resto import RestoCompany
        if RestoCompany.get():
            return RESTO_APP
        else:
            return AUTO_APP

    VERSIONS = ndb.LocalStructuredProperty(Version, repeated=True)

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

    IN_PRODUCTION = ndb.BooleanProperty(indexed=False, default=False)

    SHARE_GIFT_MODULE = ndb.LocalStructuredProperty(ShareGiftModule)
    SHARE_INVITATION_MODULE = ndb.LocalStructuredProperty(ShareInvitationModule)
    SUBSCRIPTION_MODULE = ndb.LocalStructuredProperty(SubscriptionModule)
    CLIENT_MODULE = ndb.LocalStructuredProperty(ClientModule)
    ORDER_MODULE = ndb.LocalStructuredProperty(OrderModule)
    GEO_PUSH_MODULE = ndb.LocalStructuredProperty(GeoPushModule)
    SENDING_SMS_MODULE = ndb.LocalStructuredProperty(SendingSmsModule, repeated=True)

    RBCN_MOBI = ndb.StringProperty(indexed=False)

    APP_NAME = ndb.StringProperty(indexed=False)   # todo: getting info from company module
    COMPANY_DESCRIPTION = ndb.StringProperty(indexed=False)  # suitable name is APP_DESCRIPTION
    SUPPORT_PHONE = ndb.StringProperty(indexed=False)
    SUPPORT_SITE = ndb.StringProperty(indexed=False)
    SUPPORT_EMAILS = ndb.StringProperty(indexed=False, repeated=True)
    ADDITION_INFO_ABOUT_DELIVERY = ndb.StringProperty(indexed=False)
    ANOTHER_CITY_IN_LIST = ndb.BooleanProperty(default=False)

    def get_company_dict(self):
        from methods.proxy.resto.company import get_company_info_dict
        if self.APP_KIND == AUTO_APP:
            return {
                'app_name': self.APP_NAME,
                'description': self.COMPANY_DESCRIPTION,
                'phone': self.SUPPORT_PHONE,
                'site': self.SUPPORT_SITE,
                'emails': self.SUPPORT_EMAILS
            }
        elif self.APP_KIND == RESTO_APP:
            return get_company_info_dict()

    COUNTRIES = ndb.StringProperty(indexed=False, repeated=True)
    COMPULSORY_ADDRESS_VALIDATES = ndb.BooleanProperty(indexed=False, default=False)
    COMPULSORY_DELIVERY_EMAIL_VALIDATES = ndb.BooleanProperty(indexed=False, default=False)

    REPORT_EMAILS = ndb.StringProperty(indexed=False)

    ACTION_COLOR = ndb.StringProperty(indexed=False, default='FF000000')

    def get_place_str(self):
        if self.PLACE_TYPE == VENUE:
            return u'Кофейня'
        elif self.PLACE_TYPE == BAR:
            return u'Бар'

    @property
    def SHARE_GIFT_ENABLED(self):
        from models import STATUS_AVAILABLE
        return config.SHARE_GIFT_MODULE.status == STATUS_AVAILABLE if config.SHARE_GIFT_MODULE else False

    @property
    def SHARE_INVITATION_ENABLED(self):
        from models import STATUS_AVAILABLE
        return config.SHARE_INVITATION_MODULE.status == STATUS_AVAILABLE if config.SHARE_INVITATION_MODULE else False

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

config = LocalConfigProxy()
