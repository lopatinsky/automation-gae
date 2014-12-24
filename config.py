import datetime
from google.appengine.api import app_identity


class DoubleBConfig(object):
    PROMO_ENABLED = True
    PROMO_MASTERCARD_ONLY = True
    POINTS_PER_CUP = 5
    PROMO_END_DATE = datetime.date(2015, 1, 1)
    TIMEZONE_OFFSET = datetime.timedelta(hours=3)  # TODO this is hardcoded!!!
    CANCEL_ALLOWED_BEFORE = 3


class ProductionConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://engine.paymentgate.ru/payment"
    ALFA_LOGIN = 'DoubleB_binding-api'
    ALFA_PASSWORD = 'Empatikaopen1#!'

    PROMOS_API_KEY = "NTY1OTMxMzU4NjU2OTIxNgVhFXVOYTAN9r_AM_Jrg-nwDwOj"
    FREE_COFFEE_PROMO_ID = 5634472569470976

    CITY_HAPPY_HOURS = {
        4801814507552768: {  # ftower
            "days": "12345",
            "hours": "8-11"
        },
        5656058538229760: {  # gstolic
            "days": "12345",
            "hours": "8-11"
        },
        4661077019197440: {  # tkachi
            "days": "12345",
            "hours": "9-12"
        },
        5083289484263424: {  # million
            "days": "12345",
            "hours": "9-12"
        }
    }

    DEBUG = False

    EMAILS = {
        "server": "admins",
        "order": "admins",
        "network": "admins",
    }


class TestingConfig(DoubleBConfig):
    ALFA_BASE_URL = "https://test.paymentgate.ru/testpayment"
    ALFA_LOGIN = 'empatika_autopay-api'
    ALFA_PASSWORD = 'empatika_autopay'

    PROMOS_API_KEY = "NTcxOTIzODA0NDAyNDgzMjEGJ9yK_bldMcuo0k-zMH3xktB4"
    FREE_COFFEE_PROMO_ID = 5678701068943360

    CITY_HAPPY_HOURS = {
        5629499534213120: {
            "days": "1234567",
            "hours": "0-24"
        }
    }

    DEBUG = True

    EMAILS = {
    }


if app_identity.get_application_id() == "empatika-doubleb":
    config = ProductionConfig()
else:
    config = TestingConfig()
