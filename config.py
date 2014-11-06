import datetime
from google.appengine.api import app_identity


class DoubleBConfig(object):
    PROMO_ENABLED = True
    PROMO_MASTERCARD_ONLY = True
    POINTS_PER_CUP = 5
    TIMEZONE_OFFSET = datetime.timedelta(hours=3)  # TODO this is hardcoded!!!


class ProductionConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://engine.paymentgate.ru/payment"
    ALFA_LOGIN = 'DoubleB_binding-api'
    ALFA_PASSWORD = 'Empatikaopen1#!'


class TestingConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://test.paymentgate.ru/testpayment"
    ALFA_LOGIN = 'empatika_autopay-api'
    ALFA_PASSWORD = 'empatika_autopay'


if app_identity.get_application_id() == "empatika-doubleb":
    config = ProductionConfig()
else:
    config = TestingConfig()
