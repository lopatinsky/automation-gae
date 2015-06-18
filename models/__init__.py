# coding=utf-8
STATUS_UNAVAILABLE = 0
STATUS_AVAILABLE = 1
STATUS_CHOICES = [STATUS_AVAILABLE, STATUS_UNAVAILABLE]

STATUS_MAP = {
    STATUS_UNAVAILABLE: u'недоступен',
    STATUS_AVAILABLE: u'доступен'
}

from tablet_request import TabletRequest
from error_statistics import PaymentErrorsStatistics, AlfaBankRequest
from client import Client, CardBindingPayment
from menu import SingleModifier, GroupModifier, MenuItem, MenuCategory, GroupModifierChoice
from order import Order
from payment_types import PaymentType
from promo import Promo, PromoOutcome, PromoCondition, GiftMenuItem
from share import Share, SharedGift
from specials import Notification, JsonStorage, News, Deposit
from user import User, CompanyUser, Admin, AdminStatus
from venue import Venue, DeliverySlot, DeliveryZone, Address

MINUTE_SECONDS = 60
HOUR_SECONDS = 60 * MINUTE_SECONDS
DAY_SECONDS = 24 * HOUR_SECONDS