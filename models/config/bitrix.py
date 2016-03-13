from google.appengine.ext import ndb

from models import STATUS_CHOICES, STATUS_AVAILABLE


class BitrixExtApiModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
