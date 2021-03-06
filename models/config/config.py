# coding=utf-8
from models.config.confirmation import SmsConfirmationModule
from models.config.order_message import OrderMessageModule
from models.config.sushinson import SushinSonEmailModule

SUBSCRIPTION = 0
SHARE_GIFT = 1
SHARE_INVITATION = 2
# ORDER_INFO_MODULE = 3  DEPRECATED
CLIENT_INFO_MODULE = 4
GEO_PUSH_MODULE = 5
HIT_MODULE = 6
MIVAKO_GIFT_MODULE = 7
REVIEW_MODULE = 8
MENU_FRAME_MODULE = 9
REMAINDERS_MODULE = 10
ORDER_INFO_MODULE = 11
NUMBER_OF_PEOPLE_MODULE = 12
CASH_CHANGE_MODULE = 13
CUSTOM_SECTIONS_MODULE = 14
PLATIUS_WHITE_LABEL_MODULE = 15
SMS_CONFIRMATION_MODULE = 16
CLIENT_INFO_TIP_MODULE = 17
MODULE_TYPES = (SUBSCRIPTION, SHARE_GIFT, SHARE_INVITATION, CLIENT_INFO_MODULE, HIT_MODULE, MIVAKO_GIFT_MODULE,
                REVIEW_MODULE, MENU_FRAME_MODULE, REMAINDERS_MODULE, ORDER_INFO_MODULE, NUMBER_OF_PEOPLE_MODULE,
                CASH_CHANGE_MODULE, CUSTOM_SECTIONS_MODULE, PLATIUS_WHITE_LABEL_MODULE, SMS_CONFIRMATION_MODULE,
                CLIENT_INFO_TIP_MODULE)

DEFAULT_TYPE = 0
MINIMIZED = 1
ORDER_EMAIL_FORMAT_TYPES = (DEFAULT_TYPE, MINIMIZED)

from google.appengine.api import memcache
from google.appengine.ext import ndb
from webapp2 import cached_property

from models.config.local import LocalConfigProxy
from models.config.share import ShareInvitationModule, ShareGiftModule
from models.config.field import ClientModule, OrderModule, ClientTipModule
from models.config.subscription import SubscriptionModule
from models.config.version import Version
from models.config.geo_push import GeoPushModule
from models.config.inactive_clients import InactiveNotificationModule
from models.config.menu import HitModule, MenuFrameModule, RemaindersModule
from models.config.mivako import MivakoGiftModule
from models.config.review import ReviewModule
from models.config.basket_notification import BasketNotificationModule
from models.config.custom_sections import CustomSectionsModule
from models.config.platius_wl import PlatiusWhiteLabelModule
from models.config.app_appearance import AppAppearanceIos, AppAppearanceAndroid
from models.config.bitrix import BitrixExtApiModule

OTHER = -1
VENUE = 0
BAR = 1
PLACE_TYPES = (OTHER, VENUE, BAR)

COFFEE_LOGIC = 0
MEAL_LOGIC = 1
OTHER = 2
ONLINE_STORE_LOGIC = 3
SCREEN_LOGICS = (COFFEE_LOGIC, MEAL_LOGIC, OTHER, ONLINE_STORE_LOGIC)

EMAIL_FROM = 'noreply-order@ru-beacon.ru'

AUTO_APP = 0
RESTO_APP = 1
DOUBLEB_APP = 2
APP_CHOICES = (AUTO_APP, RESTO_APP, DOUBLEB_APP)

COMPANY_IN_DEVELOPMENT = 0
COMPANY_IN_PRODUCTION = 1
COMPANY_REMOVED = 2
COMPANY_PREVIEW = 3
COMPANY_STATUS_CHOICES = (COMPANY_IN_DEVELOPMENT, COMPANY_IN_PRODUCTION, COMPANY_REMOVED, COMPANY_PREVIEW)

COMPANY_STATUS_NAMES = {
    COMPANY_IN_DEVELOPMENT: u"Не запущена",
    COMPANY_IN_PRODUCTION: u"Запущена",
    COMPANY_REMOVED: u"Отключена",
    COMPANY_PREVIEW: u"Предпросмотр в общем аппе",
}


class Config(ndb.Model):
    @cached_property
    def APP_KIND(self):
        from models.proxy.resto import RestoCompany
        from models.proxy.doubleb import DoublebCompany

        if RestoCompany.get():
            return RESTO_APP
        elif DoublebCompany.get():
            return DOUBLEB_APP
        else:
            return AUTO_APP

    VERSIONS = ndb.LocalStructuredProperty(Version, repeated=True)
    COMPANY_STATUS = ndb.IntegerProperty(indexed=False, choices=COMPANY_STATUS_CHOICES, default=COMPANY_IN_DEVELOPMENT)

    BRANCH_API_KEY = ndb.StringProperty(indexed=False)
    BRANCH_SECRET_KEY = ndb.StringProperty(indexed=False)

    CANCEL_ALLOWED_WITHIN = ndb.IntegerProperty(indexed=False, default=30)  # seconds after creation
    CANCEL_ALLOWED_BEFORE = ndb.IntegerProperty(indexed=False, default=3)  # minutes before delivery_time

    ALFA_BASE_URL = ndb.StringProperty(indexed=False, default="https://test.paymentgate.ru/testpayment")
    ALFA_LOGIN = ndb.StringProperty(indexed=False, default="empatika_autopay-api")
    ALFA_PASSWORD = ndb.StringProperty(indexed=False, default="empatika_autopay")

    PARSE_APP_API_KEY = ndb.StringProperty(indexed=False)  # todo: rewrite pushes, delete field
    PARSE_REST_API_KEY = ndb.StringProperty(indexed=False)  # todo: rewrite pushes, delete field
    PARSE_CLIENT_API_KEY = ndb.StringProperty(indexed=False)

    GOOGLE_ANALYTICS_API_KEY_IOS = ndb.StringProperty(indexed=False)
    GOOGLE_ANALYTICS_API_KEY_ANDROID = ndb.StringProperty(indexed=False)

    YANDEX_METRICA_KEY = ndb.StringProperty(indexed=False)

    EMAIL_REQUESTS = ndb.BooleanProperty(default=False)

    PROMOS_API_KEY = ndb.StringProperty(indexed=False)

    PLACE_TYPE = ndb.IntegerProperty(choices=PLACE_TYPES, default=OTHER)
    SCREEN_LOGIC = ndb.IntegerProperty(choices=SCREEN_LOGICS, default=OTHER)
    PICK_VENUE_AT_STARTUP = ndb.BooleanProperty(indexed=False, default=False)

    WALLET_API_KEY = ndb.StringProperty(indexed=False)
    WALLET_MAX_PERCENT = ndb.IntegerProperty(default=100)
    WALLET_MIN_REAL_PAYMENT = ndb.IntegerProperty(default=0)

    SHARE_GIFT_MODULE = ndb.LocalStructuredProperty(ShareGiftModule)
    SHARE_INVITATION_MODULE = ndb.LocalStructuredProperty(ShareInvitationModule)
    SUBSCRIPTION_MODULE = ndb.LocalStructuredProperty(SubscriptionModule)
    CLIENT_MODULE = ndb.LocalStructuredProperty(ClientModule)
    CLIENT_TIP_MODULE = ndb.LocalStructuredProperty(ClientTipModule)
    ORDER_MODULE = ndb.LocalStructuredProperty(OrderModule)
    GEO_PUSH_MODULE = ndb.LocalStructuredProperty(GeoPushModule)

    INACTIVE_NOTIFICATION_MODULE = ndb.LocalStructuredProperty(InactiveNotificationModule, repeated=True)
    BASKET_NOTIFICATION_MODULE = ndb.LocalStructuredProperty(BasketNotificationModule)
    SMS_CONFIRMATION_MODULE = ndb.LocalStructuredProperty(SmsConfirmationModule)

    ORDER_MESSAGE_MODULE = ndb.LocalStructuredProperty(OrderMessageModule)
    HIT_MODULE = ndb.LocalStructuredProperty(HitModule)
    MIVAKO_GIFT_MODULE = ndb.LocalStructuredProperty(MivakoGiftModule)
    REVIEW_MODULE = ndb.LocalStructuredProperty(ReviewModule)
    MENU_FRAME_MODULE = ndb.LocalStructuredProperty(MenuFrameModule)
    REMAINDERS_MODULE = ndb.LocalStructuredProperty(RemaindersModule)
    CUSTOM_SECTIONS_MODULE = ndb.LocalStructuredProperty(CustomSectionsModule)
    PLATIUS_WHITE_LABEL_MODULE = ndb.LocalStructuredProperty(PlatiusWhiteLabelModule)
    SUSHINSON_EMAIL_MODULE = ndb.LocalStructuredProperty(SushinSonEmailModule)
    BITRIX_EXT_API_MODULE = ndb.LocalStructuredProperty(BitrixExtApiModule)

    RBCN_MOBI = ndb.StringProperty(indexed=False)

    APP_NAME = ndb.StringProperty(indexed=False)  # todo: getting info from company module
    COMPANY_DESCRIPTION = ndb.StringProperty(indexed=False)  # suitable name is APP_DESCRIPTION
    SUPPORT_PHONE = ndb.StringProperty(indexed=False)
    SUPPORT_SITE = ndb.StringProperty(indexed=False)
    SUPPORT_EMAILS = ndb.StringProperty(indexed=False, repeated=True)
    ORDER_EMAIL_FORMAT_TYPE = ndb.IntegerProperty(choices=ORDER_EMAIL_FORMAT_TYPES, default=DEFAULT_TYPE, indexed=False)
    ADDITION_INFO_ABOUT_DELIVERY = ndb.StringProperty(indexed=False)
    ANOTHER_CITY_IN_LIST = ndb.BooleanProperty(default=False)
    REJECT_IF_NOT_IN_ZONES = ndb.BooleanProperty(default=False)
    COMPANY_LOGO_URL = ndb.StringProperty(indexed=False)

    def get_company_dict(self):
        from methods.proxy.resto.company import get_company_info_dict

        company_dict = {
            'logo_url': self.COMPANY_LOGO_URL
        }
        if self.APP_KIND in [AUTO_APP, DOUBLEB_APP]:
            company_dict.update({
                'app_name': self.APP_NAME,
                'description': self.COMPANY_DESCRIPTION,
                'phone': self.SUPPORT_PHONE,
                'site': self.SUPPORT_SITE,
                'emails': self.SUPPORT_EMAILS
            })
        elif self.APP_KIND == RESTO_APP:
            company_dict.update(get_company_info_dict())

        return company_dict

    COUNTRIES = ndb.StringProperty(indexed=False, repeated=True)
    COMPULSORY_ADDRESS_VALIDATES = ndb.BooleanProperty(indexed=False, default=False)
    COMPULSORY_DELIVERY_EMAIL_VALIDATES = ndb.BooleanProperty(indexed=False, default=False)

    REPORT_EMAILS = ndb.StringProperty(indexed=False)
    REPORT_WEEKLY = ndb.BooleanProperty(default=False)

    ACTION_COLOR = ndb.StringProperty(indexed=False, default='FF000000')
    APP_APPEARANCE_IOS = ndb.LocalStructuredProperty(AppAppearanceIos)
    APP_APPEARANCE_ANDROID = ndb.LocalStructuredProperty(AppAppearanceAndroid)

    def get_place_str(self):
        if self.PLACE_TYPE == VENUE:
            return u'Кофейня'
        elif self.PLACE_TYPE == BAR:
            return u'Бар'
        else:
            return u'Заведение'

    @property
    def GET_APP_APPEARANCE_IOS(self):
        if not self.APP_APPEARANCE_IOS:
            self.APP_APPEARANCE_IOS = AppAppearanceIos()
            config.put()
        return self.APP_APPEARANCE_IOS

    @property
    def GET_APP_APPEARANCE_ANDROID(self):
        if not self.APP_APPEARANCE_ANDROID:
            self.APP_APPEARANCE_ANDROID = AppAppearanceAndroid()
            config.put()
        return self.APP_APPEARANCE_ANDROID

    @property
    def SHARE_GIFT_ENABLED(self):
        return ShareGiftModule.has_module()

    @property
    def SHARE_INVITATION_ENABLED(self):
        return ShareInvitationModule.has_module(self)

    @property
    def WALLET_ENABLED(self):
        return self.WALLET_API_KEY is not None

    @classmethod
    def GET_MAX_WALLET_SUM(cls, total_sum):  # must be positive
        config = cls.get()
        percent = total_sum * config.WALLET_MAX_PERCENT / 100.0
        max_percent = total_sum - config.WALLET_MIN_REAL_PAYMENT
        if max_percent < 0:
            return 0.0
        elif percent > max_percent:
            return max_percent
        else:
            return percent

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
