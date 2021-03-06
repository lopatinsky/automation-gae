# coding=utf-8
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth import models

from google.appengine.ext.ndb import polymodel

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
            'id': self.key.id(),
            'login': self.login
        }


class CompanyUser(User):
    ROLE = 'company'

    # these are numbers of bits for individual privileges
    RIGHTS_BIT_REPORT = 0
    RIGHTS_BIT_VENUE = 1
    RIGHTS_BIT_MENU = 2
    RIGHTS_BIT_PAYMENT_TYPE = 3
    RIGHTS_BIT_PROMOS = 4
    RIGHTS_BIT_BARISTA = 5
    RIGHTS_BIT_PROMO_CODE = 6
    RIGHTS_BIT_COMPANY_INFO = 7
    RIGHTS_BIT_LEGAL = 8
    RIGHTS_BIT_DELIVERY = 9
    RIGHTS_BIT_DELIVERY_TYPES = 10
    RIGHTS_BIT_ZONES = 12
    RIGHTS_BIT_NEWS = 13
    RIGHTS_BIT_PUSHES = 14
    RIGHTS_BIT_ALFA = 15
    RIGHTS_BIT_USERS = 16
    RIGHTS_BIT_CONFIG = 17

    ALL_RIGHTS_BITS = (RIGHTS_BIT_REPORT, RIGHTS_BIT_VENUE, RIGHTS_BIT_MENU, RIGHTS_BIT_PAYMENT_TYPE, RIGHTS_BIT_PROMOS,
                       RIGHTS_BIT_BARISTA, RIGHTS_BIT_PROMO_CODE, RIGHTS_BIT_COMPANY_INFO, RIGHTS_BIT_LEGAL,
                       RIGHTS_BIT_DELIVERY, RIGHTS_BIT_DELIVERY_TYPES, RIGHTS_BIT_ZONES, RIGHTS_BIT_NEWS,
                       RIGHTS_BIT_PUSHES, RIGHTS_BIT_ALFA, RIGHTS_BIT_USERS, RIGHTS_BIT_CONFIG)

    # these are commonly used combined masks
    # 63 bits for admins -- so we can put this into datastore and freely add new rights
    RIGHTS_MASK_ADMIN = 0x7fffffffffffffff

    rights = ndb.IntegerProperty(indexed=False, required=True)

    def has_all_rights(self):
        return self.rights == self.RIGHTS_MASK_ADMIN

    @staticmethod
    def make_mask(bits):
        return sum(1 << bit for bit in bits)

    def has_rights(self, required_bits):
        required_mask = self.make_mask(required_bits)
        return self.rights & required_mask == required_mask


class Admin(User):
    ROLE = 'admin'

    venue = ndb.KeyProperty(Venue, indexed=True)  # None for global admin, actual venue for barista
    deposit_history = ndb.StructuredProperty(Deposit, repeated=True)

    def query_orders(self, *args, **kwargs):
        from models.order import Order

        if self.venue:
            return Order.query(Order.venue_id == str(self.venue.id()), *args, **kwargs)
        return Order.query(*args, **kwargs)

    def order_by_id(self, order_id):
        from models.order import Order

        order = Order.get_by_id(order_id)
        if not order:
            return None
        if self.venue and order.venue_id != str(self.venue.id()):
            return None
        return order

    def get_sources(self):
        return [deposit.source for deposit in self.deposit_history]

    def delete_auth_ids(self):
        class_name = type(self).__name__
        ids = ["%s.auth_id:%s" % (class_name, i) for i in self.auth_ids]
        self.unique_model.delete_multi(ids)

    @property
    def venue_entity(self):
        if self.venue:
            return Venue.get(self.venue.id())
        return None

    def dict(self):
        result = super(Admin, self).dict()
        result.update({
            'venue': self.venue_entity.dict()
        })
        return result


class Courier(User):
    ROLE = 'courier'

    admin = ndb.KeyProperty(kind=Admin)
    name = ndb.StringProperty()
    surname = ndb.StringProperty()

    def dict(self):
        result = super(Courier, self).dict()
        result.update({
            'name': self.name,
            'surname': self.surname
        })
        return result

    def query_orders(self, *args, **kwargs):
        from models.order import Order

        return Order.query(Order.courier == self.key, *args, **kwargs)

    def order_by_id(self, order_id):
        from models.order import Order

        order = Order.get_by_id(order_id)
        if not order:
            return None
        if order.courier != self.key:
            return None
        return order


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


MAP_RIGHTS = {
    CompanyUser.RIGHTS_BIT_REPORT: u'Отчеты',
    CompanyUser.RIGHTS_BIT_VENUE: u'Кофейни',
    CompanyUser.RIGHTS_BIT_MENU: u'Меню',
    CompanyUser.RIGHTS_BIT_PAYMENT_TYPE: u'Типы оплат',
    CompanyUser.RIGHTS_BIT_PROMOS: u'Акции',
    CompanyUser.RIGHTS_BIT_BARISTA: u'Баристы',
    CompanyUser.RIGHTS_BIT_PROMO_CODE: u'Промо коды',
    CompanyUser.RIGHTS_BIT_COMPANY_INFO: u'Инфо о компании',
    CompanyUser.RIGHTS_BIT_LEGAL: u'Юр. иформация',
    CompanyUser.RIGHTS_BIT_DELIVERY: u'Доставка',
    CompanyUser.RIGHTS_BIT_DELIVERY_TYPES: u'Типы доставок',
    CompanyUser.RIGHTS_BIT_ZONES: u'Зоны',
    CompanyUser.RIGHTS_BIT_NEWS: u'Новости',
    CompanyUser.RIGHTS_BIT_PUSHES: u'Пуши',
    CompanyUser.RIGHTS_BIT_ALFA: u'Альфа',
    CompanyUser.RIGHTS_BIT_USERS: u'Пользователи',
    CompanyUser.RIGHTS_BIT_CONFIG: u'Конфигурация',
}
