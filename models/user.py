from google.appengine.ext import ndb
from webapp2_extras.appengine.auth import models
from google.appengine.ext.ndb import polymodel
from models.order import Order
from models.specials import Deposit
from models.venue import Venue

__author__ = 'dvpermyakov'


class User(polymodel.PolyModel, models.User):
    namespace = ndb.StringProperty(default='')
    login = ndb.StringProperty()

    def get_role(self):
        return NotImplemented


class CompanyUser(User):
    ROLE = 'company'

    def get_role(self):
        return self.ROLE


class Admin(User):
    ROLE = 'admin'

    venue = ndb.KeyProperty(Venue, indexed=True)  # None for global admin, actual venue for barista
    deposit_history = ndb.StructuredProperty(Deposit, repeated=True)

    def get_role(self):
        return self.ROLE

    def query_orders(self, *args, **kwargs):
        if self.venue:
            return Order.query(Order.venue_id == self.venue.id(), *args, **kwargs)
        return Order.query(*args, **kwargs)

    def order_by_id(self, order_id):
        order = Order.get_by_id(order_id)
        if not order:
            return None
        if self.venue and order.venue_id != self.venue.id():
            return None
        return order

    def get_sources(self):
        return [deposit.source for deposit in self.deposit_history]

    def delete_auth_ids(self):
        class_name = type(self).__name__
        ids = ["%s.auth_id:%s" % (class_name, i) for i in self.auth_ids]
        self.unique_model.delete_multi(ids)


class AdminStatus(ndb.Model):
    location = ndb.GeoPtProperty()
    time = ndb.DateTimeProperty(auto_now=True)
    readonly = ndb.BooleanProperty(default=False)

    @staticmethod
    def _make_key_name(uid, token):
        return "%s_%s" % (uid, token)

    @classmethod
    def create(cls, uid, token, location, readonly):
        key_name = cls._make_key_name(uid, token)
        entity = cls(id=key_name, location=location, readonly=readonly)
        entity.put()
        return entity

    @classmethod
    def get(cls, uid, token):
        key_name = cls._make_key_name(uid, token)
        return cls.get_by_id(key_name)

    @property
    def admin_id(self):
        return int(self.key.id().split("_")[0])

    @property
    def admin(self):
        return Admin.get_by_id(self.admin_id)

    @property
    def token(self):
        return self.key.id().split("_")[1]