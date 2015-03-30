import datetime
from google.appengine.api import app_identity


class DoubleBConfig(object):
    TIMEZONE_OFFSET = datetime.timedelta(hours=3)  # TODO this is hardcoded!!!

    CANCEL_ALLOWED_WITHIN = 30  # seconds after creation
    CANCEL_ALLOWED_BEFORE = 3  # minutes before delivery_time

    CARD_BINDING_REQUIRED = True
    GEOPUSH_SEND_RADIUS = 500


class ProductionConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://engine.paymentgate.ru/payment"
    ALFA_LOGIN = ''
    ALFA_PASSWORD = ''

    WALLET_API_KEY = "NTY1OTMxMzU4NjU2OTIxNsN7jorhvqRjzwKVYGSxDVSX5raI"

    DEBUG = False

    BRANCH_IO_TAG = 'production'

    EMAILS = {
        "server": "admins",
        "order": "admins",
        "network": "admins",
        "analytics": "admins",
        "ping": "admins",
        "receipt": "dvpermyakov1@gmail.com"
    }


class TestingConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://test.paymentgate.ru/testpayment"
    ALFA_LOGIN = 'empatika_autopay-api'
    ALFA_PASSWORD = 'empatika_autopay'

    WALLET_API_KEY = "NTYzNDQ3MjU2OTQ3MDk3Nt5XvGjSyGwIzlf7F-SjVSdv9LyF"

    DEBUG = True
    BRANCH_IO_TAG = 'test'

    EMAILS = {
        "receipt": "dvpermyakov1@gmail.com"
    }


if app_identity.get_application_id() == "doubleb-automation-production":
    config = ProductionConfig()
else:
    config = TestingConfig()
