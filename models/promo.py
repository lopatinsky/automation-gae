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
    CHOICES = [DISCOUNT, CASH_BACK, DISCOUNT_CHEAPEST, DISCOUNT_RICHEST, ACCUMULATE_GIFT_POINT, ORDER_GIFT,
               ORDER_ACCUMULATE_GIFT_POINT]

    item = ndb.KeyProperty(kind=MenuItem)  # item_required is False => apply for all items
    item_required = ndb.BooleanProperty(default=True)
    method = ndb.IntegerProperty(choices=CHOICES, required=True)
    value = ndb.IntegerProperty(required=True)


class PromoCondition(ndb.Model):
    CHECK_TYPE_DELIVERY = 0
    CHECK_FIRST_ORDER = 1
    CHECK_MAX_ORDER_SUM = 2
    CHECK_ITEM_IN_ORDER = 3
    CHECK_REPEATED_ORDERS = 4
    CHOICES = [CHECK_TYPE_DELIVERY, CHECK_FIRST_ORDER, CHECK_MAX_ORDER_SUM, CHECK_ITEM_IN_ORDER, CHECK_REPEATED_ORDERS]

    item = ndb.KeyProperty(kind=MenuItem)  # item_required is False => apply for all items
    item_required = ndb.BooleanProperty(default=True)
    method = ndb.IntegerProperty(choices=CHOICES, required=True)
    value = ndb.IntegerProperty()


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
            elif outcome.method in [PromoOutcome.CASH_BACK]:
                icon = self._get_url(hostname, self.CASHBACK_ICON)
            elif outcome.method in [PromoOutcome.DISCOUNT, PromoOutcome.DISCOUNT_CHEAPEST, PromoOutcome.DISCOUNT_RICHEST]:
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