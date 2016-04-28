from google.appengine.ext import ndb

from models import STATUS_CHOICES, STATUS_AVAILABLE


class BitrixExtApiModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    url = ndb.StringProperty(required=True, indexed=False)
    constant_params = ndb.JsonProperty(required=True, default={})
    param_name = ndb.StringProperty(required=True, default='url', indexed=False)
