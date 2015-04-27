import threading
from google.appengine.ext import ndb


class Config(ndb.Model):
    CANCEL_ALLOWED_WITHIN = ndb.IntegerProperty(indexed=False, default=30)  # seconds after creation
    CANCEL_ALLOWED_BEFORE = ndb.IntegerProperty(indexed=False, default=3)  # minutes before delivery_time

    CARD_BINDING_REQUIRED = True
    
    ALFA_BASE_URL = ndb.StringProperty(indexed=False, default="https://test.paymentgate.ru/testpayment")
    ALFA_LOGIN = ndb.StringProperty(indexed=False, default="empatika_autopay-api")
    ALFA_PASSWORD = ndb.StringProperty(indexed=False, default="empatika_autopay")

    WALLET_API_KEY = ndb.StringProperty(indexed=False)

    @property
    def WALLET_ENABLED(self):
        return self.WALLET_API_KEY is not None

    EMAILS = ndb.JsonProperty(default={
        "server": "admins",
    })

    password = ndb.StringProperty()

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
