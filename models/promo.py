# coding=utf-8
from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_UNAVAILABLE
from models.menu import MenuItem

__author__ = 'dvpermyakov'


class GiftMenuItem(ndb.Model):   # self.key.id() == item.key.id()
    item = ndb.KeyProperty(kind=MenuItem, required=True)
    status = ndb.IntegerProperty(choices=[STATUS_AVAILABLE, STATUS_UNAVAILABLE], default=STATUS_AVAILABLE)
    promo_id = ndb.IntegerProperty(required=True)  # it relates to empatika-promos
    points = ndb.IntegerProperty(required=True)  # how many spent

    def dict(self):
        dict = self.item.get().dict()
        dict.update({
            'points': self.points
        })
        return dict


class PromoOutcome(ndb.Model):
    DISCOUNT = 0               # calculated by prices
    CASH_BACK = 1              # calculated by prices
    DISCOUNT_CHEAPEST = 2      # calculated by prices ## use priority to imply in the end
    DISCOUNT_RICHEST = 3       # calculated by prices ## use priority to imply in the end
    ACCUMULATE_GIFT_POINT = 4
    ORDER_GIFT = 5
    ORDER_ACCUMULATE_GIFT_POINT = 6
    FIX_DISCOUNT = 7
    CASH_BACK_WITHOUT_WALLET_PAYMENT = 8
    CHOICES = (DISCOUNT, CASH_BACK, DISCOUNT_CHEAPEST, DISCOUNT_RICHEST, ACCUMULATE_GIFT_POINT, ORDER_GIFT,
               ORDER_ACCUMULATE_GIFT_POINT, FIX_DISCOUNT, CASH_BACK_WITHOUT_WALLET_PAYMENT)

    item = ndb.KeyProperty(kind=MenuItem)  # item_required is False => apply for all items
    item_required = ndb.BooleanProperty(default=False)
    method = ndb.IntegerProperty(choices=CHOICES, required=True)
    value = ndb.IntegerProperty(required=True)


class PromoCondition(ndb.Model):
    CHECK_TYPE_DELIVERY = 0
    CHECK_FIRST_ORDER = 1
    CHECK_MAX_ORDER_SUM = 2
    CHECK_ITEM_IN_ORDER = 3
    CHECK_REPEATED_ORDERS = 4
    CHECK_MIN_ORDER_SUM = 5
    CHECK_HAPPY_HOURS = 6
    CHOICES = (CHECK_TYPE_DELIVERY, CHECK_FIRST_ORDER, CHECK_MAX_ORDER_SUM, CHECK_ITEM_IN_ORDER, CHECK_REPEATED_ORDERS,
               CHECK_MIN_ORDER_SUM, CHECK_HAPPY_HOURS)

    item = ndb.KeyProperty(kind=MenuItem)  # item_required is False => apply for all items
    item_required = ndb.BooleanProperty(default=False)
    method = ndb.IntegerProperty(choices=CHOICES, required=True)
    value = ndb.IntegerProperty()
    hh_days = ndb.StringProperty()   # it is used only for happy hours
    hh_hours = ndb.StringProperty()  # it is used only for happy hours


class Promo(ndb.Model):
    def _get_url(self, hostname, param):
        return u'http://%s/%s' % (hostname, param)

    BONUS_ICON = u'images/promo_icons/bonus.png'
    CASHBACK_ICON = u'images/promo_icons/cashback.png'
    DISCOUNT_ICON = u'images/promo_icons/discount.png'
    GIFT_ICON = u'images/promo_icons/gift.png'

    title = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    conditions = ndb.StructuredProperty(PromoCondition, repeated=True)
    outcomes = ndb.StructuredProperty(PromoOutcome, repeated=True)

    conflicts = ndb.KeyProperty(repeated=True)  # kind=Promo  # Not Implemented
    priority = ndb.IntegerProperty(default=0)                 # Not Implemented
    more_one = ndb.BooleanProperty(default=True)              # Not Implemented
    status = ndb.IntegerProperty(choices=[STATUS_AVAILABLE, STATUS_UNAVAILABLE], default=STATUS_AVAILABLE)

    def dict(self, hostname):
        icon = None
        if self.outcomes:
            outcome = self.outcomes[0]
            if outcome.method in [PromoOutcome.ACCUMULATE_GIFT_POINT, PromoOutcome.ORDER_ACCUMULATE_GIFT_POINT]:
                icon = self._get_url(hostname, self.BONUS_ICON)
            elif outcome.method in [PromoOutcome.CASH_BACK, PromoOutcome.CASH_BACK_WITHOUT_WALLET_PAYMENT]:
                icon = self._get_url(hostname, self.CASHBACK_ICON)
            elif outcome.method in [PromoOutcome.DISCOUNT, PromoOutcome.DISCOUNT_CHEAPEST, PromoOutcome.DISCOUNT_RICHEST,
                                    PromoOutcome.FIX_DISCOUNT]:
                icon = self._get_url(hostname, self.DISCOUNT_ICON)
            elif outcome.method in [PromoOutcome.ORDER_GIFT]:
                icon = self._get_url(hostname, self.GIFT_ICON)
        return {
            'id': self.key.id(),
            'title': self.title,
            'description': self.description,
            'icon': icon
        }

    def validation_dict(self):
        return {
            'id': self.key.id(),
            'text': self.title
        }

CONDITION_MAP = {
    PromoCondition.CHECK_FIRST_ORDER: u"Первый заказ",
    PromoCondition.CHECK_TYPE_DELIVERY: u"Тип доставки",
    PromoCondition.CHECK_MAX_ORDER_SUM: u'Максимальная сумма заказа',
    PromoCondition.CHECK_ITEM_IN_ORDER: u'Продукт в заказе',
    PromoCondition.CHECK_REPEATED_ORDERS: u'Повторный заказ',
    PromoCondition.CHECK_MIN_ORDER_SUM: u'Минимальная сумма заказа',
    PromoCondition.CHECK_HAPPY_HOURS: u'Счастливые часы'
}

OUTCOME_MAP = {
    PromoOutcome.CASH_BACK: u"Кэшбек",
    PromoOutcome.DISCOUNT: u"Скидка",
    PromoOutcome.DISCOUNT_RICHEST: u'Скидка на самый дорогой продукт в заказе',
    PromoOutcome.DISCOUNT_CHEAPEST: u'Скидка на самый дешевый продукт в заказе',
    PromoOutcome.ACCUMULATE_GIFT_POINT: u'Баллы',
    PromoOutcome.ORDER_GIFT: u'Подарок',
    PromoOutcome.ORDER_ACCUMULATE_GIFT_POINT: u'Баллы за заказ',
    PromoOutcome.FIX_DISCOUNT: u'Фиксированная скидка',
    PromoOutcome.CASH_BACK_WITHOUT_WALLET_PAYMENT: u'Кэшбек без учета оплаты кошельком'
}