# coding=utf-8
import logging
from google.appengine.ext import ndb
from methods import fastcounter
from methods.rendering import timestamp, latinize
from models import STATUS_AVAILABLE
from models.geo_push import GeoPush
from models.promo_code import PromoCodePerforming
from models.share import SharedGift
from models.client import Client
from models.menu import GroupModifier, MenuItem, SingleModifier
from models.payment_types import CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE, PAYMENT_TYPE_CHOICES
from models.promo import Promo, GiftMenuItem
from models.specials import Subscription
from models.user import Courier
from models.venue import Venue, DeliveryZone, Address, DeliverySlot

NEW_ORDER = 0
READY_ORDER = 1
CANCELED_BY_CLIENT_ORDER = 2
CANCELED_BY_BARISTA_ORDER = 3
CREATING_ORDER = 4
CONFIRM_ORDER = 5
ON_THE_WAY = 6

STATUSES = (NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER, CREATING_ORDER, CONFIRM_ORDER,
            ON_THE_WAY)
NOT_CANCELED_STATUSES = (NEW_ORDER, READY_ORDER, CONFIRM_ORDER, ON_THE_WAY)  # not include CREATING_ORDER

STATUS_MAP = {
    NEW_ORDER: u"Новый",
    READY_ORDER: u"Выдан",
    CANCELED_BY_CLIENT_ORDER: u"Отменен клиентом",
    CANCELED_BY_BARISTA_ORDER: u"Отменен бариста",
    CREATING_ORDER: u'Заказ с ошибкой оплаты',
    CONFIRM_ORDER: u'Подтвержденный заказ',
    ON_THE_WAY: u'В пути'
}

CONFUSED_TIME = 0
CONFUSED_VENUE = 1
CONFUSED_SELF = 2
CONFUSED_OTHER = 3
CONFUSED_CHOICES = (CONFUSED_VENUE, CONFUSED_TIME, CONFUSED_SELF, CONFUSED_OTHER)


class SubscriptionDetails(ndb.Model):
    subscription = ndb.KeyProperty(kind=Subscription, required=True)
    amount = ndb.IntegerProperty(required=True)


class CashBack(ndb.Model):
    READY = 0
    DONE = 1

    amount = ndb.IntegerProperty(required=True)
    status = ndb.IntegerProperty(choices=[READY, DONE], default=READY)


class ChosenGroupModifierDetails(ndb.Model):
    group_modifier = ndb.KeyProperty(kind=GroupModifier)
    group_choice_id = ndb.IntegerProperty()
    group_choice_id_str = ndb.StringProperty()  # todo: set group_choice_id to str

    def group_modifier_obj(self):
        choice_id = self.group_choice_id if self.group_choice_id else self.group_choice_id_str
        return self.group_modifier, choice_id

    @property
    def title(self):
        return '%s(%s)' % (self.group_modifier.get().title, self.group_modifier.get().get_choice_by_id(self.group_choice_id).title)

    @property
    def float_price(self):
        return self.group_modifier.get().get_choice_by_id(self.group_choice_id).price / 100.0


class OrderPositionDetails(ndb.Model):
    item = ndb.KeyProperty(MenuItem, required=True)
    price = ndb.IntegerProperty(required=True)  # в копейках
    revenue = ndb.FloatProperty(required=True)
    promos = ndb.KeyProperty(kind=Promo, repeated=True)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_modifiers = ndb.StructuredProperty(ChosenGroupModifierDetails, repeated=True)


class GiftPositionDetails(ndb.Model):
    gift = ndb.KeyProperty(kind=GiftMenuItem, required=True)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_modifiers = ndb.StructuredProperty(ChosenGroupModifierDetails, repeated=True)
    activation_id = ndb.IntegerProperty(required=True)


class SharedGiftPositionDetails(ndb.Model):
    gift = ndb.KeyProperty(kind=SharedGift)


class GiftPointsDetails(ndb.Model):
    READY = 0
    DONE = 1

    item = ndb.KeyProperty(kind=MenuItem)  # applied for all items in order if not placed
    points = ndb.IntegerProperty(required=True)
    status = ndb.IntegerProperty(choices=[READY, DONE], default=READY)


class Order(ndb.Model):
    from models.client import DEVICE_CHOICES
    number = ndb.IntegerProperty(required=True)
    client_id = ndb.IntegerProperty(required=True)
    user_agent = ndb.StringProperty()
    total_sum = ndb.FloatProperty(indexed=False)
    payment_sum = ndb.FloatProperty(indexed=False)
    status = ndb.IntegerProperty(required=True, choices=STATUSES, default=CREATING_ORDER)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    delivery_type = ndb.IntegerProperty()
    delivery_time = ndb.DateTimeProperty()
    delivery_time_str = ndb.StringProperty()
    delivery_sum = ndb.IntegerProperty(default=0)
    delivery_slot_id = ndb.IntegerProperty()
    delivery_zone = ndb.KeyProperty(kind=DeliveryZone)
    payment_type_id = ndb.IntegerProperty(required=True, choices=PAYMENT_TYPE_CHOICES)
    wallet_payment = ndb.FloatProperty(required=True, default=0.0)
    coordinates = ndb.GeoPtProperty(indexed=False)
    venue_id = ndb.StringProperty(required=True)
    pan = ndb.StringProperty(indexed=False)
    return_comment = ndb.StringProperty(indexed=False)
    comment = ndb.StringProperty(indexed=False)
    return_datetime = ndb.DateTimeProperty()
    payment_id = ndb.StringProperty()
    device_type = ndb.IntegerProperty(choices=DEVICE_CHOICES, required=True)
    address = ndb.LocalStructuredProperty(Address)
    item_details = ndb.LocalStructuredProperty(OrderPositionDetails, repeated=True)
    order_gift_details = ndb.LocalStructuredProperty(OrderPositionDetails, repeated=True)
    gift_details = ndb.LocalStructuredProperty(GiftPositionDetails, repeated=True)
    shared_gift_details = ndb.LocalStructuredProperty(SharedGiftPositionDetails, repeated=True)
    points_details = ndb.LocalStructuredProperty(GiftPointsDetails, repeated=True)
    subscription_details = ndb.LocalStructuredProperty(SubscriptionDetails)
    promo_code_performings = ndb.KeyProperty(kind=PromoCodePerforming, repeated=True)
    promos = ndb.KeyProperty(kind=Promo, repeated=True, indexed=False)
    actual_delivery_time = ndb.DateTimeProperty(indexed=False)
    response_success = ndb.BooleanProperty(default=False, indexed=False)
    first_for_client = ndb.BooleanProperty()
    cash_backs = ndb.StructuredProperty(CashBack, repeated=True)
    cancel_reason = ndb.IntegerProperty(choices=CONFUSED_CHOICES)
    cancel_reason_text = ndb.StringProperty()
    email_key_done = ndb.StringProperty()
    email_key_cancel = ndb.StringProperty()
    email_key_postpone = ndb.StringProperty()
    email_key_confirm = ndb.StringProperty()
    courier = ndb.KeyProperty(kind=Courier)
    geo_push = ndb.KeyProperty(kind=GeoPush)
    extra_data = ndb.JsonProperty()
    unified_app_namespace = ndb.StringProperty()

    @classmethod
    def get(cls, client):
        from models.config.config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.history import get_orders
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            return cls.query(cls.client_id == client.key.id())
        elif app_kind == RESTO_APP:
            return get_orders(client)

    def activate_cash_back(self):
        from methods.empatika_wallet import deposit, get_balance
        from google.appengine.ext.deferred import deferred
        total_cash_back = 0
        for cash_back in self.cash_backs:
            if cash_back.status == cash_back.READY:
                total_cash_back += cash_back.amount
                cash_back.status = cash_back.DONE
        if total_cash_back > 0:
            logging.info('cash back with sum=%s' % total_cash_back)
            deposit(self.client_id, total_cash_back, "order_id_%s" % self.key.id())
            deferred.defer(get_balance, self.client_id, raise_error=True)  # just to update memcache
        self.put()
        return total_cash_back

    def activate_gift_points(self):
        from methods import empatika_promos
        point_sum = 0
        for index, point_detail in enumerate(self.points_details):
            if point_detail.status == GiftPointsDetails.READY:
                empatika_promos.register_order(self.client_id, point_detail.points, '%s_%s' % (self.key.id(), index))
                point_detail.status = GiftPointsDetails.DONE
                point_sum += point_detail.points
        self.put()
        return point_sum

    @staticmethod
    def grouped_item_dict(details, gift=False):
        from models.menu import MenuItem
        item_dicts = []
        for item_detail in details:
            if not gift:
                item = MenuItem.get(item_detail.item.id())
                gift_obj = None
            else:
                gift_obj = item_detail.gift.get()
                if gift_obj:
                    item = gift_obj.item.get()
                else:
                    logging.warning('Gift is not found = %s' % item_detail.gift)
                    item = None
            if not item:
                continue
            item_dicts.append({
                'item': item,
                'points': gift_obj.points if gift_obj else None,
                'price': item_detail.price if not gift_obj else 0,
                'image': item.picture,
                'single_modifier_keys':  item_detail.single_modifiers,
                'group_modifier_keys': [modifier.group_modifier_obj() for modifier in item_detail.group_modifiers]
            })
        from methods.orders.validation.validation import group_item_dicts
        response = []
        for index, group_dict in enumerate(group_item_dicts(item_dicts)):
            response_dict = {
                "id": group_dict['id'],
                "title": group_dict['title'],
                "price": group_dict['price_without_promos'] / 100.0,  # в рублях
                "image": group_dict.get('image'),
                "pic": group_dict.get('image'),
                "quantity": group_dict['quantity'],
                "single_modifiers": group_dict['single_modifiers'],
                "group_modifiers": group_dict['group_modifiers']
            }
            if item_dicts[index]['points']:
                response_dict['points'] = item_dicts[index]['points']
            response.append(response_dict)
        return response

    def status_dict(self):
        dct = {
            'order_id': str(self.key.id()),
            'number': self.number,
            'status': self.status
        }
        return dct

    def history_dict(self):
        dct = self.status_dict()
        if self.delivery_slot_id:
            delivery_slot = DeliverySlot.get_by_id(self.delivery_slot_id)
        else:
            delivery_slot = None
        gifts = self.grouped_item_dict(self.gift_details, gift=True)
        gifts.extend(self.grouped_item_dict(self.order_gift_details))
        dct.update({
            "delivery_type": self.delivery_type,
            "address": self.address.dict() if self.address else None,
            "delivery_time": timestamp(self.delivery_time) if self.delivery_time else 0,
            "delivery_time_str": self.delivery_time_str,
            "delivery_slot": delivery_slot.dict() if delivery_slot else None,
            "delivery_slot_str": delivery_slot.name if delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS
            else None,
            "payment_type_id": self.payment_type_id,
            "total": self.total_sum,
            "menu_sum": sum([item_detail.price / 100.0 for item_detail in self.item_details]),
            "wallet_payment": self.wallet_payment,
            "delivery_sum": self.delivery_sum,
            "venue_id": str(self.venue_id),
            "venue": Venue.get(self.venue_id).admin_dict(),
            "items": self.grouped_item_dict(self.item_details),
            "gifts": gifts
        })
        return dct

    def dict(self, extra_fields_in_comment=True):
        dct = self.history_dict()
        client = Client.get(self.client_id)
        dct.update({
            "total_sum": self.total_sum,
            "actual_delivery_time": timestamp(self.actual_delivery_time) if self.actual_delivery_time else None,
            "client": client.dict(with_extra_fields=not extra_fields_in_comment),
            "pan": self.pan,
            "comment": self.get_comment(client, extra_fields=extra_fields_in_comment),
            "return_comment": self.return_comment
        })
        return dct

    def get_comment(self, client, extra_fields):
        from models.config.config import config

        comment = self.comment
        if extra_fields:
            if config.CLIENT_MODULE and config.CLIENT_MODULE.status == STATUS_AVAILABLE:
                for field in config.CLIENT_MODULE.extra_fields:
                    value = client.extra_data and client.extra_data.get(latinize(field.title))
                    comment += "; %s: %s" % (field.title, value)
            if config.ORDER_MODULE and config.ORDER_MODULE.status == STATUS_AVAILABLE:
                for field in config.ORDER_MODULE.extra_fields:
                    value = self.extra_data and self.extra_data.get(latinize(field.title))
                    if value:
                        comment += "; %s: %s" % (field.title, value)
        return comment

    @staticmethod
    def generate_id():
        value = fastcounter.get_count("order_id")
        fastcounter.incr("order_id")
        return value + 1

    @property
    def has_card_payment(self):
        return bool(self.payment_type_id == CARD_PAYMENT_TYPE and self.payment_id)

    @property
    def has_paypal_payment(self):
        return bool(self.payment_type_id == PAYPAL_PAYMENT_TYPE and self.payment_id)