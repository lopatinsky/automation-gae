from google.appengine.ext import ndb
from webapp2_extras.appengine.auth import models
from google.appengine.ext.ndb import polymodel
from models.order import Order, ON_THE_WAY
from models.specials import Deposit
from models.venue import Venue

__author__ = 'dvpermyakov'


class User(polymodel.PolyModel, models.User):
    ROLE = None

    namespace = ndb.StringProperty(default='')
    login = ndb.StringProperty()

    def get_role(self):
        return self.ROLE

    def dict(self):
        return {
            'login': self.login
        }


class CompanyUser(User):
    ROLE = 'company'


class Admin(User):
    ROLE = 'admin'

    venue = ndb.KeyProperty(Venue, indexed=True)  # None for global admin, actual venue for barista
    deposit_history = ndb.StructuredProperty(Deposit, repeated=True)

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

    def dict(self):
        dict = super(Admin, self).dict()
        dict.update({
            'venue': self.venue.get().dict()
        })
        return dict


class Courier(User):
    ROLE = 'courier'

    admin = ndb.KeyProperty(kind=Admin)
    name = ndb.StringProperty()
    surname = ndb.StringProperty()

    def dict(self):
        dict = super(Courier, self).dict()
        dict.update({
            'name': self.name,
            'surname': self.surname
        })
        return dict

    def query_orders(self, *args, **kwargs):
        return Order.query(Order.venue_id == self.admin.get().venue.id(), Order.status == ON_THE_WAY, *args, **kwargs)


class UserStatus(ndb.Model):
    time = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def create(cls, uid, token, location=None, readonly=None):
        pass

    @staticmethod
    def _make_key_name(uid, token):
        return "%s_%s" % (uid, token)

    @classmethod
    def get(cls, uid, token):
        key_name = cls._make_key_name(uid, token)
        return cls.get_by_id(key_name)

    @property
    def user_id(self):
        return int(self.key.id().split("_")[0])

    @property
    def token(self):
        return self.key.id().split("_")[1]

    @property
    def user(self):
        return User.get_by_id(self.user_id)


class AdminStatus(UserStatus):
    location = ndb.GeoPtProperty()
    readonly = ndb.BooleanProperty(default=False)

    @classmethod
    def create(cls, uid, token, location=None, readonly=None):
        key_name = cls._make_key_name(uid, token)
        entity = cls(id=key_name, location=location, readonly=readonly)
        entity.put()
        return entity

    @property
    def user(self):
        return Admin.get_by_id(self.user_id)


class CourierStatus(UserStatus):

    @classmethod
    def create(cls, uid, token, location=None, readonly=None):
        key_name = cls._make_key_name(uid, token)
        entity = cls(id=key_name)
        entity.put()
        return entity

    @property
    def user(self):
        return Courier.get_by_id(self.user_id)