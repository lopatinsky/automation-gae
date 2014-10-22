import datetime
from google.appengine.api import app_identity


class DoubleBConfig(object):
    PROMO_ENABLED = True
    PROMO_MASTERCARD_ONLY = True
    POINTS_PER_CUP = 6
    TIMEZONE_OFFSET = datetime.timedelta(hours=4)  # TODO this is hardcoded!!!


class ProductionConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://engine.paymentgate.ru/payment"


class TestingConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://test.paymentgate.ru/testpayment"


if app_identity.get_application_id() == "empatika-doubleb":
    config = TestingConfig()  # TODO use ProductionConfig here
else:
    config = TestingConfig()
