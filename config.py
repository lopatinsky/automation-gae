import datetime
from google.appengine.api import app_identity


class DoubleBConfig(object):
    PROMO_ENABLED = True
    PROMO_MASTERCARD_ONLY = True
    POINTS_PER_CUP = 5
    PROMO_END_DATE = datetime.date(2015, 2, 28)
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
        5224026972618752: {  # alkon
            "days": "12345",
            "hours": "8-12",
        },
        4661077019197440: {  # tkachi
            "days": "12345",
            "hours": "9-12"
        },
        5083289484263424: {  # million
            "days": "12345",
            "hours": "9-12"
        },
        5313962648272896: {  # kronv
            "days": "12345",
            "hours": "9-12"
        },
    }

    STOP_LISTS = {
        5093108584808448: [15, 26, 27], # omega
    }
    SPECIALS = {
        37: [  # grapefruit tea
            1,  # mil
            4801814507552768,  # ftower
            5656058538229760,  # gstolic
            5660980839186432,  # dmitr
            5786976926040064,  # tvyamsk
            5083289484263424,  # million
        ],
    }

    DEBUG = False

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

    PROMOS_API_KEY = "NTcxOTIzODA0NDAyNDgzMjEGJ9yK_bldMcuo0k-zMH3xktB4"
    FREE_COFFEE_PROMO_ID = 5678701068943360

    CITY_HAPPY_HOURS = {
        5629499534213120: {
            "days": "1234567",
            "hours": "0-24"
        }
    }

    STOP_LISTS = {
    }
    SPECIALS = {
        6: [
            5707702298738688,
            5629499534213120,
        ],
    }

    DEBUG = True

    EMAILS = {
        "receipt": "dvpermyakov1@gmail.com"
    }


if app_identity.get_application_id() == "empatika-doubleb":
    config = ProductionConfig()
else:
    config = TestingConfig()
