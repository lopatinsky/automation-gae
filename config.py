from google.appengine.api import app_identity


class DoubleBConfig(object):
    pass


class ProductionConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://engine.paymentgate.ru/payment"


class TestingConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://test.paymentgate.ru/testpayment"


if app_identity.get_application_id() == "empatika-doubleb":
    config = TestingConfig()  # TODO use ProductionConfig here
else:
    config = TestingConfig()
