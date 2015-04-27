# coding=utf-8

import datetime
import logging
import random
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from webapp2_extras.appengine.auth import models
from methods import location, fastcounter, working_hours
from methods.rendering import timestamp, opt
from tablet_request import TabletRequest
from error_statistics import PaymentErrorsStatistics, AlfaBankRequest
from config import config
from methods.empatika_promos import register_order


CASH_PAYMENT_TYPE = 0
CARD_PAYMENT_TYPE = 1
BONUS_PAYMENT_TYPE = 2

STATUS_AVAILABLE = 1
STATUS_UNAVAILABLE = 0

NEW_ORDER = 0
READY_ORDER = 1
CANCELED_BY_CLIENT_ORDER = 2
CANCELED_BY_BARISTA_ORDER = 3
CREATING_ORDER = 4

IOS_DEVICE = 0
ANDROID_DEVICE = 1

PUSH_NOTIFICATION = 0
SMS_SUCCESS = 1
SMS_PASSIVE = 2

SINGLE_MODIFIER = 0
GROUP_MODIFIER = 1

SELF = 0
IN_CAFE = 1


class SingleModifier(ndb.Model):
    title = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(required=True)
    min_amount = ndb.IntegerProperty(default=0)
    max_amount = ndb.IntegerProperty(default=0)

    def dict(self):
        return {
            'modifier_id': str(self.key.id()),
            'title': self.title,
            'price': self.price,
            'min': self.min_amount,
            'max': self.max_amount
        }


class GroupModifierChoice(ndb.Model):
    choice_id = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(default=0)

    @staticmethod
    def generate_id():
        fastcounter.incr("group_choice_id", delta=100, update_interval=1)
        return fastcounter.get_count("group_choice_id") + random.randint(1, 100)

    @classmethod
    def create(cls, title, price):
        choice = cls(choice_id=GroupModifierChoice.generate_id(), title=title, price=price)
        choice.put()
        return choice

    @classmethod
    def get_by_choice_id(cls, choice_id):  # use outside of group_modifier
        return cls.query(cls.choice_id == choice_id).get()

    def get_group_modifier(self):  # use outside of group_modifier
        return GroupModifier.get_modifier_by_choice(self.choice_id)


class GroupModifier(ndb.Model):
    title = ndb.StringProperty(required=True)
    choices = ndb.StructuredProperty(GroupModifierChoice, repeated=True)

    def get_choice_by_id(self, choice_id):
        for choice in self.choices:
            if choice_id == choice.choice_id:
                return choice
        return None

    @classmethod
    def get_modifier_by_choice(cls, choice_id):
        for modifier in cls.query().fetch():
            for choice in modifier.choices:
                if choice.choice_id == choice_id:
                    return modifier
        return None

    def dict(self, product=None):
        choices = [choice for choice in self.choices
                   if product is None or choice.choice_id not in product.group_choice_restrictions]
        return {
            'modifier_id': str(self.key.id()),
            'title': self.title,
            'choices': [
                {
                    'title': choice.title,
                    'price': choice.price,
                    'id': str(choice.choice_id)
                } for choice in choices
            ]
        }


class MenuItem(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    description = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=False)
    kal = ndb.IntegerProperty(indexed=False)
    cost_price = ndb.IntegerProperty(default=0)  # TODO: what is it?
    weight = ndb.FloatProperty(indexed=False)
    volume = ndb.FloatProperty(indexed=False)
    price = ndb.IntegerProperty(required=True, indexed=False)
    status = ndb.IntegerProperty(required=True, choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE),
                                 default=STATUS_AVAILABLE)
    sequence_number = ndb.IntegerProperty(default=0)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_modifiers = ndb.KeyProperty(kind=GroupModifier, repeated=True)

    restrictions = ndb.KeyProperty(repeated=True)  # kind=Venue (permanent use)
    group_choice_restrictions = ndb.IntegerProperty(repeated=True)  # GroupModifierChoice.choice_id
    stop_list_group_choices = ndb.IntegerProperty(repeated=True)    # GroupModifierChoice.choice_id

    def dict(self, without_restrictions=False):
        dct = {
            'id': str(self.key.id()),
            'order': self.sequence_number,
            'title': self.title,
            'description': self.description,
            'price':  self.price,
            'kal': self.kal,
            'pic': self.picture,
            'weight': self.weight,
            'volume': self.volume,
            'single_modifiers': [modifier.get().dict() for modifier in self.single_modifiers],
            'group_modifiers': [modifier.get().dict(self) for modifier in self.group_modifiers],
            'restrictions': {
                'venues': [str(restrict.id()) for restrict in self.restrictions]
            }
        }
        if without_restrictions:
            del dct['restrictions']
        return dct


class MenuCategory(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    picture = ndb.StringProperty(indexed=False)
    menu_items = ndb.KeyProperty(kind=MenuItem, repeated=True, indexed=False)
    status = ndb.IntegerProperty(choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE), default=STATUS_AVAILABLE)

    restrictions = ndb.KeyProperty(repeated=True)  # kind=Venue not implemented

    def generate_sequence_number(self):
        fastcounter.incr("category_%s" % self.key.id(), delta=100, update_interval=1)
        return fastcounter.get_count("category_%s" % self.key.id()) + random.randint(1, 100)

    def get_items_in_order(self):
        return sorted([item.get() for item in self.menu_items], key=lambda item: item.sequence_number)

    def get_previous(self, item):
        items = self.get_items_in_order()
        if item not in items:
            return None
        index = items.index(item)
        if index == 0:
            return None
        else:
            return items[index - 1]

    def get_next(self, item):
        items = self.get_items_in_order()
        if item not in items:
            return None
        index = items.index(item)
        if index == len(items) - 1:
            return None
        else:
            return items[index + 1]

    def dict(self, venue=None):
        items = []
        for item in self.menu_items:
            item = item.get()
            if item.status != STATUS_AVAILABLE:
                continue
            if not venue:
                items.append(item.dict())
            else:
                if venue.key not in item.restrictions:
                    items.append(item.dict(without_restrictions=True))
        dct = {
            'info': {
                'category_id': str(self.key.id()),
                'title': self.title,
                'pic': self.picture,
                'restrictions': {
                    'venues': [str(restrict.id()) for restrict in self.restrictions]
                }
            },
            'items': items
        }
        if venue:
            del dct['info']['restrictions']
        return dct


class PromoOutcome(ndb.Model):
    DISCOUNT = 0           # calculated by prices
    CASH_BACK = 1          # calculated by prices
    DISCOUNT_CHEAPEST = 2  # calculated by prices ## use priority to imply in the end
    DISCOUNT_RICHEST = 3   # calculated by prices ## use priority to imply in the end

    item = ndb.KeyProperty(kind=MenuItem)  # item_required is False => apply for all items
    item_required = ndb.BooleanProperty(default=True)
    method = ndb.IntegerProperty(choices=[DISCOUNT, CASH_BACK, DISCOUNT_CHEAPEST, DISCOUNT_RICHEST], required=True)
    value = ndb.IntegerProperty(required=True)


class PromoCondition(ndb.Model):
    CHECK_TYPE_DELIVERY = 0
    CHECK_FIRST_ORDER = 1

    item = ndb.KeyProperty(kind=MenuItem)  # item_required is False => apply for all items
    item_required = ndb.BooleanProperty(default=True)
    method = ndb.IntegerProperty(choices=[CHECK_TYPE_DELIVERY, CHECK_FIRST_ORDER], required=True)
    value = ndb.IntegerProperty()


class Promo(ndb.Model):
    title = ndb.StringProperty(required=True)
    title_for_user = ndb.StringProperty()
    description = ndb.StringProperty()
    conditions = ndb.StructuredProperty(PromoCondition, repeated=True)
    outcomes = ndb.StructuredProperty(PromoOutcome, repeated=True)

    conflicts = ndb.KeyProperty(repeated=True)  # kind=Promo  # Not Implemented
    priority = ndb.IntegerProperty(default=0)
    more_one = ndb.BooleanProperty(default=True)              # Not Implemented
    status = ndb.IntegerProperty(choices=[STATUS_AVAILABLE, STATUS_UNAVAILABLE], default=STATUS_AVAILABLE)

    def dict(self):
        return {
            'id': self.key.id(),
            'title': self.title,
            'description': self.description
        }

    def validation_dict(self):
        return {
            'id': self.key.id(),
            'text': self.title_for_user if self.title_for_user else self.title
        }


class CashBack(ndb.Model):
    READY = 0
    DONE = 1

    amount = ndb.IntegerProperty(required=True)
    status = ndb.IntegerProperty(choices=[READY, DONE], default=READY)


class Venue(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    description = ndb.StringProperty(indexed=False)
    pic = ndb.StringProperty(indexed=False)
    coordinates = ndb.GeoPtProperty(required=True, indexed=False)
    working_days = ndb.StringProperty(indexed=False)
    working_hours = ndb.StringProperty(indexed=False)
    takeout_only = ndb.BooleanProperty(indexed=False, default=False)
    phone_numbers = ndb.StringProperty(repeated=True, indexed=False)
    holiday_schedule = ndb.StringProperty(indexed=False)
    problem = ndb.StringProperty(indexed=False)
    active = ndb.BooleanProperty(required=True, default=False)
    type_deliveries = ndb.IntegerProperty(repeated=True)
    timezone_offset = ndb.IntegerProperty(default=3)  # hours offset
    stop_lists = ndb.KeyProperty(kind=MenuItem, repeated=True)
    single_modifiers_stop_list = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_choice_modifier_stop_list = ndb.KeyProperty(kind=GroupModifierChoice, repeated=True)
    promo_restrictions = ndb.KeyProperty(kind=Promo, repeated=True)

    def dynamic_info(self):
        items = []
        for item in self.stop_lists:
            item = item.get()
            if item.status != STATUS_AVAILABLE and self.key in item.restrictions:
                continue
            items.append(str(item.key.id()))
        return {
            'stop_list': {
                'items': items,
                'single_modifiers': [str(item.id()) for item in self.single_modifiers_stop_list],
                'group_modifier_choices': [str(item.get().choice_id) for item in self.group_choice_modifier_stop_list]
            }
        }

    def dict(self, user_location=None):
        distance = 0
        if user_location:
            distance = location.distance(user_location, self.coordinates)
        dct = {
            'id': str(self.key.id()),
            'distance': distance,
            'title': self.title,
            'address': self.description,
            'pic': self.pic,
            'lat': self.coordinates.lat,
            'lon': self.coordinates.lon,
            'coordinates': str(self.coordinates),
            'is_open': self.is_open(),
            'takeout_only': self.takeout_only,
            'schedule': []
        }
        working_days = self.working_days.split(',')
        working_hours = self.working_hours.split(',')
        for i in xrange(len(working_days)):
            dct['schedule'].append({'days': [int(day) for day in working_days[i]],
                                    'hours': working_hours[i]})
        return dct

    def admin_dict(self):
        return {
            'id': self.key.id(),
            'title': self.title,
            'address': self.description
        }

    def is_open(self, minutes_offset=0):
        now = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes_offset) + datetime.timedelta(hours=self.timezone_offset)
        return working_hours.check(self.working_days, self.working_hours, now, self.holiday_schedule)


class ChosenGroupModifierDetails(ndb.Model):
    group_modifier = ndb.KeyProperty(kind=GroupModifier)
    group_choice_id = ndb.IntegerProperty()

    def group_modifier_obj(self):
        return self.group_modifier, self.group_choice_id


class OrderPositionDetails(ndb.Model):
    item = ndb.KeyProperty(MenuItem, required=True)
    price = ndb.IntegerProperty(required=True)
    revenue = ndb.FloatProperty(required=True)
    promos = ndb.KeyProperty(kind=Promo, repeated=True)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_modifiers = ndb.StructuredProperty(ChosenGroupModifierDetails, repeated=True)


class Order(ndb.Model):
    client_id = ndb.IntegerProperty(required=True)
    total_sum = ndb.FloatProperty(indexed=False)
    payment_sum = ndb.FloatProperty(indexed=False)
    status = ndb.IntegerProperty(required=True, choices=(NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER,
                                                         CANCELED_BY_BARISTA_ORDER, CREATING_ORDER),
                                 default=CREATING_ORDER)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    delivery_time = ndb.DateTimeProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=(CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE,
                                                                  BONUS_PAYMENT_TYPE))
    wallet_payment = ndb.FloatProperty(required=True, default=0.0)
    coordinates = ndb.GeoPtProperty(indexed=False)
    venue_id = ndb.IntegerProperty(required=True)
    pan = ndb.StringProperty(indexed=False)
    return_comment = ndb.StringProperty(indexed=False)
    comment = ndb.StringProperty(indexed=False)
    return_datetime = ndb.DateTimeProperty()
    payment_id = ndb.StringProperty()
    device_type = ndb.IntegerProperty(required=True)
    items = ndb.KeyProperty(indexed=False, repeated=True, kind=MenuItem)
    item_details = ndb.LocalStructuredProperty(OrderPositionDetails, repeated=True)
    promos = ndb.KeyProperty(kind=Promo, repeated=True, indexed=False)
    actual_delivery_time = ndb.DateTimeProperty(indexed=False)
    response_success = ndb.BooleanProperty(default=False, indexed=False)
    first_for_client = ndb.BooleanProperty()

    cash_backs = ndb.StructuredProperty(CashBack, repeated=True)

    def activate_cash_back(self):
        logging.info("activate_cash_back")
        from methods.empatika_wallet import deposit
        for cash_back in self.cash_backs:
            if cash_back.status == cash_back.READY:
                deposit(self.client_id, cash_back.amount, "order_id_%s" % self.key.id())
                cash_back.status = cash_back.DONE
        self.put()

    def dict(self):
        dct = {
            "order_id": self.key.id(),
            "total_sum": self.total_sum,
            "venue": Venue.get_by_id(self.venue_id).admin_dict(),
            "status": self.status,
            "delivery_time": timestamp(self.delivery_time),
            "actual_delivery_time": opt(timestamp, self.actual_delivery_time),
            "payment_type_id": self.payment_type_id,
            "client": Client.get_by_id(self.client_id).dict(),
            "pan": self.pan,
            "comment": self.comment,
            "return_comment": self.return_comment,
            "items": []
        }
        item_dicts = []
        for item_detail in self.item_details:
            item = item_detail.item.get()
            item_dicts.append({
                'item': item,
                'price': item_detail.price,
                'image': item.picture,
                'single_modifier_keys':  item_detail.single_modifiers,
                'group_modifier_keys': [modifier.group_modifier_obj() for modifier in item_detail.group_modifiers]
            })

        from methods.orders.validation import group_item_dicts
        for item_dict in group_item_dicts(item_dicts):
            dct["items"].append({
                "id": item_dict['id'],
                "title": item_dict['title'],
                "price": item_dict['price_without_promos'],
                "image": item_dict.get('image'),
                "quantity": item_dict['quantity'],
                "single_modifiers": item_dict['single_modifiers'],
                "group_modifiers": item_dict['group_modifiers']
            })
        return dct

    def status_dict(self):
        dct = {
            'order_id': str(self.key.id()),
            'status': self.status
        }

        return dct

    def history_dict(self):
        dct = {
            "order_id": str(self.key.id()),
            "status": self.status,
            "delivery_time": timestamp(self.delivery_time),
            "payment_type_id": self.payment_type_id,
            "total": self.total_sum,
            "venue_id": str(self.venue_id),
            "items": []
        }

        item_dicts = []
        for item_detail in self.item_details:
            item_dicts.append({
                'item': item_detail.item.get(),
                'price': item_detail.price,
                'single_modifier_keys':  item_detail.single_modifiers,
                'group_modifier_keys': [modifier.group_modifier_obj() for modifier in item_detail.group_modifiers]
            })

        from methods.orders.validation import group_item_dicts
        for item_dict in group_item_dicts(item_dicts):
            dct["items"].append({
                "id": item_dict['id'],
                "title": item_dict['title'],
                "price": item_dict['price_without_promos'],
                "quantity": item_dict['quantity'],
                "single_modifiers": item_dict['single_modifiers'],
                "group_modifiers": item_dict['group_modifiers']
            })
        return dct

    @staticmethod
    def generate_id():
        value = fastcounter.get_count("order_id")
        fastcounter.incr("order_id")
        return value + 1


class Notification(ndb.Model):
    client_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    type = ndb.IntegerProperty(required=True, choices=(PUSH_NOTIFICATION, SMS_SUCCESS, SMS_PASSIVE))


class Client(ndb.Model):
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    tel = ndb.StringProperty()
    email = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

    name_confirmed = ndb.BooleanProperty(default=False)
    name_for_sms = ndb.StringProperty(default='')

    user_agent = ndb.StringProperty(indexed=False)
    tied_card = ndb.BooleanProperty(default=False)
    device_phone = ndb.StringProperty()

    @classmethod
    def create(cls):
        return cls(id=cls.generate_id())

    @staticmethod
    def generate_id():
        value = fastcounter.get_count("client_id")
        fastcounter.incr("client_id")
        return value + 1

    def dict(self):
        return {
            "id": self.key.id(),
            "name": self.name,
            "surname": self.surname,
            "phone": self.tel
        }


class PaymentType(ndb.Model):
    title = ndb.StringProperty(indexed=False)
    status = ndb.IntegerProperty(required=True, choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE),
                                 default=STATUS_AVAILABLE)

    def dict(self):
        dct = {
            'id': int(self.key.id()),
            'title': self.title
        }

        return dct


class News(ndb.Model):
    text = ndb.StringProperty(required=True, indexed=False)
    image_url = ndb.StringProperty(required=True, indexed=False)
    active = ndb.BooleanProperty(required=True, default=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    def dict(self):
        dct = {
            "id": self.key.id(),
            "text": self.text,
            "created_at": timestamp(self.created_at)
        }
        if self.image_url:
            dct["image_url"] = self.image_url
        return dct


class Deposit(ndb.Model):
    source = ndb.StringProperty(required=True)


class User(polymodel.PolyModel, models.User):
    pass


class CompanyUser(User):
    login = ndb.StringProperty()


class Admin(User):
    email = ndb.StringProperty(required=True, indexed=False)
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

    @property
    def login(self):
        return self.email

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


class JsonStorage(ndb.Model):
    data = ndb.JsonProperty()

    @classmethod
    def get(cls, storage_id):
        entity = cls.get_by_id(storage_id)
        if entity:
            return entity.data
        return None

    @classmethod
    def save(cls, storage_id, data):
        if data is None:
            cls.delete(storage_id)
        else:
            cls(id=storage_id, data=data).put()

    @classmethod
    def delete(cls, storage_id):
        ndb.Key(cls, storage_id).delete()


class CardBindingPayment(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    client_id = ndb.IntegerProperty()
    success = ndb.BooleanProperty()  # None if status unknown
    error = ndb.IntegerProperty()  # None if error unknown
    error_description = ndb.StringProperty()

    @property
    def order_id(self):
        return self.key.id()


class Share(ndb.Model):
    from methods.branch_io import SHARE, INVITATION, GIFT

    ACTIVE = 0
    INACTIVE = 1

    sender = ndb.KeyProperty(required=True, kind=Client)
    share_type = ndb.IntegerProperty(required=True, choices=[SHARE, INVITATION, GIFT])
    created = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.IntegerProperty(default=ACTIVE)
    urls = ndb.StringProperty(repeated=True)

    def deactivate(self):
        self.status = self.INACTIVE
        self.put()


class SharedFreeCup(ndb.Model):  # free cup is avail after recipient orders smth and should be deleted after that
    READY = 0
    DONE = 1

    sender = ndb.KeyProperty(required=True, kind=Client)
    recipient = ndb.KeyProperty(required=True, kind=Client)
    share_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.IntegerProperty(choices=[READY, DONE], default=READY)

    def deactivate_cup(self):
        order_id = "referral_%s" % self.recipient.id()
        register_order(user_id=self.sender.id(), points=config.POINTS_PER_CUP, order_id=order_id)
        self.status = self.DONE
        self.put()


class SharedGift(ndb.Model):
    READY = 0
    DONE = 1

    created = ndb.DateTimeProperty(auto_now_add=True)
    share_id = ndb.IntegerProperty(required=True)
    client_id = ndb.IntegerProperty(required=True)  # Who pays for cup
    recipient_id = ndb.IntegerProperty()
    total_sum = ndb.IntegerProperty(required=True)
    order_id = ndb.StringProperty(required=True)
    payment_type_id = ndb.IntegerProperty(required=True, choices=(CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE,
                                                                  BONUS_PAYMENT_TYPE))
    payment_id = ndb.StringProperty(required=True)
    status = ndb.IntegerProperty(choices=[READY, DONE], default=READY)

    def deactivate_cup(self, client):
        register_order(user_id=client.key.id(), points=config.POINTS_PER_CUP,
                       order_id=self.order_id)
        share = Share.get_by_id(self.share_id)
        share.deactivate()
        self.status = self.DONE
        self.recipient_id = client.key.id()
        self.put()