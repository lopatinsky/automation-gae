# coding=utf-8
import random

from google.appengine.api import memcache
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb

from methods import fastcounter
from models import STATUS_AVAILABLE, STATUS_UNAVAILABLE, GroupModifier, STATUS_CHOICES
from models.menu import MenuItem, SingleModifier
from models.schedule import Schedule

__author__ = 'dvpermyakov'


class GiftMenuItem(ndb.Model):  # self.key.id() == item.key.id()
    item = ndb.KeyProperty(kind=MenuItem, required=True)
    status = ndb.IntegerProperty(choices=[STATUS_AVAILABLE, STATUS_UNAVAILABLE], default=STATUS_AVAILABLE)
    promo_id = ndb.IntegerProperty(required=True)  # it relates to empatika-promos
    points = ndb.IntegerProperty(required=True)  # how many spent
    additional_group_choice_restrictions = ndb.IntegerProperty(repeated=True)

    def dict(self):
        result = memcache.get('gift_items_%s_%s' % (namespace_manager.get_namespace(), self.key.id()))
        if not result:
            item = self.item.get()
            result = item.dict()
            result['id'] = str(self.key.id())
            result.update({
                'points': self.points
            })
            for modifier in result['group_modifiers']:
                choice_dicts = modifier['choices']
                for choice_dict in choice_dicts[:]:
                    if int(choice_dict['id']) in self.additional_group_choice_restrictions:
                        choice_dict['price'] = 0
                        modifier['choices'] = [choice_dict]
                        break
            for modifier in result['single_modifiers'][:]:
                if modifier['price'] > 0:
                    result['single_modifiers'].remove(modifier)
            if self.additional_group_choice_restrictions:
                result['title'] = u'%s %s' % (item.title, u','.join(
                    [GroupModifier.get_modifier_by_choice(choice).get_choice_by_id(choice).title for choice in
                     self.additional_group_choice_restrictions]))
            memcache.set('gift_items_%s_%s' % (namespace_manager.get_namespace(), self.key.id()), result,
                         time=24 * 3600)
        return result


class PromoMenuItem(ndb.Model):
    item = ndb.KeyProperty(kind=MenuItem)
    group_choice_ids = ndb.IntegerProperty(repeated=True)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)


class PromoOutcome(ndb.Model):
    DISCOUNT = 0
    CASH_BACK = 1
    DISCOUNT_CHEAPEST = 2
    DISCOUNT_RICHEST = 3
    ACCUMULATE_GIFT_POINT = 4
    ORDER_GIFT = 5
    ORDER_ACCUMULATE_GIFT_POINT = 6
    FIX_DISCOUNT = 7
    DELIVERY_SUM_DISCOUNT = 8
    DELIVERY_FIX_SUM_DISCOUNT = 9
    PERCENT_GIFT_POINT = 10
    SET_PERSISTENT_MARK = 11
    REMOVE_PERSISTENT_MARK = 12
    MARKED_ORDER_GIFT = 13
    EMPTY = 14
    CASH_ACCUMULATE_GIFT_POINT = 15
    FORBID_MENU_ITEM = 16
    MARKED_DISCOUNT_CHEAPEST = 17
    DELIVERY_MESSAGE = 18
    FIX_CASH_BACK = 19
    FORBID_MENU_CATEGORY = 20
    MARKED_DISCOUNT = 21
    MARKED_ACCUMULATE_GIFT_POINT = 22
    MARKED_FIX_DISCOUNT_CHEAPEST = 23
    FORBID_ORDER = 24
    CHOICES = (DISCOUNT, CASH_BACK, DISCOUNT_CHEAPEST, DISCOUNT_RICHEST, ACCUMULATE_GIFT_POINT, ORDER_GIFT,
               ORDER_ACCUMULATE_GIFT_POINT, FIX_DISCOUNT, DELIVERY_SUM_DISCOUNT, DELIVERY_FIX_SUM_DISCOUNT,
               PERCENT_GIFT_POINT, SET_PERSISTENT_MARK, REMOVE_PERSISTENT_MARK, MARKED_ORDER_GIFT, EMPTY,
               CASH_ACCUMULATE_GIFT_POINT, FORBID_MENU_ITEM, MARKED_DISCOUNT_CHEAPEST, DELIVERY_MESSAGE, FIX_CASH_BACK,
               FORBID_MENU_CATEGORY, MARKED_DISCOUNT, MARKED_ACCUMULATE_GIFT_POINT, MARKED_FIX_DISCOUNT_CHEAPEST,
               FORBID_ORDER)

    item_details = ndb.LocalStructuredProperty(PromoMenuItem)
    method = ndb.IntegerProperty(choices=CHOICES, required=True)
    value = ndb.IntegerProperty(required=True)
    message = ndb.StringProperty()
    error_message = ndb.StringProperty()


class PromoCondition(ndb.Model):
    CHECK_TYPE_DELIVERY = 0
    CHECK_FIRST_ORDER = 1
    CHECK_MAX_ORDER_SUM = 2
    CHECK_ITEM_IN_ORDER = 3
    CHECK_REPEATED_ORDERS = 4
    CHECK_MIN_ORDER_SUM = 5
    CHECK_HAPPY_HOURS = 6
    CHECK_MIN_ORDER_SUM_WITH_PROMOS = 7
    CHECK_GROUP_MODIFIER_CHOICE = 8
    CHECK_NOT_GROUP_MODIFIER_CHOICE = 9
    CHECK_PAYMENT_TYPE = 10
    CHECK_HAPPY_HOURS_CREATED_TIME = 11
    MARK_ITEM_WITH_CATEGORY = 12
    MARK_ITEM_WITHOUT_CATEGORY = 13
    CHECK_MARKED_MIN_SUM = 14
    MARK_ITEM = 15
    MARK_NOT_ITEM = 16
    MARK_ITEM_WITH_QUANTITY = 17
    CHECK_PROMO_CODE = 18
    CHECK_ORDER_NUMBER = 19
    CHECK_ITEM_NOT_IN_ORDER = 20
    CHECK_MARKED_QUANTITY = 21
    CHECK_DEVICE_TYPE = 22
    CHECK_VERSION = 23
    CHECK_GEO_PUSH = 24
    CHECK_VENUE = 25
    CHECK_MARK = 26
    CHECK_REPEATED_ORDER_BEFORE = 27
    CHECK_MAX_USES = 28
    CHECK_MIN_DATE = 29
    CHECK_MAX_DATE = 30
    CHECK_LEFT_BASKET_PROMO = 31
    CHECK_INVITED_USER = 32
    CHECK_USER_INVITED = 33
    CHECK_DISH_HAS_GROUP_MODIFIERS = 34
    CHECK_DISH_HAS_NO_GROUP_MODIFIERS = 35
    CHECK_IS_DELIVERY_ZONE = 36
    CHECK_IS_NOT_DELIVERY_ZONE = 37
    CHECK_REGISTRATION_DATE = 38
    CHOICES = (CHECK_TYPE_DELIVERY, CHECK_FIRST_ORDER, CHECK_MAX_ORDER_SUM, CHECK_ITEM_IN_ORDER, CHECK_REPEATED_ORDERS,
               CHECK_MIN_ORDER_SUM, CHECK_HAPPY_HOURS, CHECK_MIN_ORDER_SUM_WITH_PROMOS, CHECK_GROUP_MODIFIER_CHOICE,
               CHECK_NOT_GROUP_MODIFIER_CHOICE, CHECK_PAYMENT_TYPE, CHECK_HAPPY_HOURS_CREATED_TIME,
               MARK_ITEM_WITH_CATEGORY, MARK_ITEM_WITHOUT_CATEGORY, CHECK_MARKED_MIN_SUM, MARK_ITEM, MARK_NOT_ITEM,
               MARK_ITEM_WITH_QUANTITY, CHECK_PROMO_CODE, CHECK_ORDER_NUMBER, CHECK_ITEM_NOT_IN_ORDER,
               CHECK_MARKED_QUANTITY, CHECK_DEVICE_TYPE, CHECK_VERSION, CHECK_GEO_PUSH, CHECK_VENUE, CHECK_MARK,
               CHECK_REPEATED_ORDER_BEFORE, CHECK_MAX_USES, CHECK_MIN_DATE, CHECK_MAX_DATE, CHECK_LEFT_BASKET_PROMO,
               CHECK_INVITED_USER, CHECK_USER_INVITED, CHECK_DISH_HAS_GROUP_MODIFIERS,
               CHECK_DISH_HAS_NO_GROUP_MODIFIERS, CHECK_IS_DELIVERY_ZONE, CHECK_IS_NOT_DELIVERY_ZONE,
               CHECK_REGISTRATION_DATE)

    item_details = ndb.LocalStructuredProperty(PromoMenuItem)
    method = ndb.IntegerProperty(choices=CHOICES, required=True)
    value = ndb.IntegerProperty()
    schedule = ndb.LocalStructuredProperty(Schedule)


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

    image = ndb.StringProperty(indexed=False)

    conflicts = ndb.KeyProperty(repeated=True)  # kind=Promo
    priority = ndb.IntegerProperty()
    more_one = ndb.BooleanProperty(default=True)  # Not Implemented
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    visible = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    hide_in_list = ndb.BooleanProperty(default=False)

    start = ndb.DateTimeProperty()
    end = ndb.DateTimeProperty()

    @classmethod
    def query_promos(cls, *args, **kwargs):  # AUTO_APP = 0
        from models.config.config import config, AUTO_APP, RESTO_APP, DOUBLEB_APP
        from methods.proxy.resto.promo import get_promos

        app_kind = config.APP_KIND
        if app_kind in [AUTO_APP, DOUBLEB_APP]:
            return cls.query(*args, **kwargs).fetch()
        elif app_kind == RESTO_APP:
            promos = get_promos()
            for promo in promos[:]:
                for name, value in kwargs.items():
                    if getattr(promo, name) != value:
                        promos.remove(promo)
            return promos

    @staticmethod
    def generate_priority():
        fastcounter.incr("promo", delta=100, update_interval=1)
        return fastcounter.get_count("promo") + random.randint(1, 100)

    @classmethod
    def get_promos_in_order(cls):
        return sorted([promo for promo in cls.query().fetch()], key=lambda promo: -promo.priority)

    def get_previous(self):
        promos = self.get_promos_in_order()
        index = promos.index(self)
        if index == 0:
            return None
        else:
            return promos[index - 1]

    def get_next(self):
        promos = self.get_promos_in_order()
        index = promos.index(self)
        if index == len(promos) - 1:
            return None
        else:
            return promos[index + 1]

    def _get_icon_url(self, hostname):
        icon = None
        if self.outcomes:
            outcome = self.outcomes[0]
            if outcome.method in [PromoOutcome.ACCUMULATE_GIFT_POINT, PromoOutcome.ORDER_ACCUMULATE_GIFT_POINT,
                                  PromoOutcome.PERCENT_GIFT_POINT, PromoOutcome.CASH_ACCUMULATE_GIFT_POINT]:
                icon = self._get_url(hostname, self.BONUS_ICON)
            elif outcome.method in [PromoOutcome.CASH_BACK]:
                icon = self._get_url(hostname, self.CASHBACK_ICON)
            elif outcome.method in [PromoOutcome.DISCOUNT, PromoOutcome.DISCOUNT_CHEAPEST,
                                    PromoOutcome.DISCOUNT_RICHEST,
                                    PromoOutcome.FIX_DISCOUNT, PromoOutcome.DELIVERY_SUM_DISCOUNT,
                                    PromoOutcome.DELIVERY_FIX_SUM_DISCOUNT, PromoOutcome.MARKED_DISCOUNT_CHEAPEST]:
                icon = self._get_url(hostname, self.DISCOUNT_ICON)
            elif outcome.method in [PromoOutcome.ORDER_GIFT, PromoOutcome.MARKED_ORDER_GIFT]:
                icon = self._get_url(hostname, self.GIFT_ICON)
        return icon

    def dict(self, hostname):
        return {
            'id': self.key.id(),
            'title': self.title,
            'description': self.description,
            'icon': self.image or self._get_icon_url(hostname),
            'is_icon': not self.image
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
    PromoCondition.CHECK_HAPPY_HOURS: u'Счастливые часы время заказа',
    PromoCondition.CHECK_MIN_ORDER_SUM_WITH_PROMOS: u'Минимальная сумма с учетом акций',
    PromoCondition.CHECK_GROUP_MODIFIER_CHOICE: u'Выбор группового модификатора в заказе',
    PromoCondition.CHECK_NOT_GROUP_MODIFIER_CHOICE: u'Выбора группового модификатора нет в заказе',
    PromoCondition.CHECK_PAYMENT_TYPE: u'Тип оплаты',
    PromoCondition.CHECK_HAPPY_HOURS_CREATED_TIME: u'Счастливые часы время создания заказа',
    PromoCondition.MARK_ITEM_WITH_CATEGORY: u'(метка) Пометить только продукты из данной категории',
    PromoCondition.MARK_ITEM_WITHOUT_CATEGORY: u'(метка) Пометить продукты не из данной категории',
    PromoCondition.CHECK_MARKED_MIN_SUM: u'(метка) Минимальная сумма помеченных продуктов',
    PromoCondition.MARK_ITEM: u'(метка) Пометить только данный продукт',
    PromoCondition.MARK_NOT_ITEM: u'(метка) Пометить все, кроме данного продукта',
    PromoCondition.MARK_ITEM_WITH_QUANTITY: u'(метка) Минимальное кол-во помеченных продуктов каждого типа',
    PromoCondition.CHECK_PROMO_CODE: u'Клиент активировал промо-код из группы',
    PromoCondition.CHECK_ORDER_NUMBER: u'Кратный N заказ клиента',
    PromoCondition.CHECK_ITEM_NOT_IN_ORDER: u'Продукта нет в заказе',
    PromoCondition.CHECK_MARKED_QUANTITY: u'(метка) Минимальное кол-во помеченных продуктов',
    PromoCondition.CHECK_DEVICE_TYPE: u'Тип телефона',
    PromoCondition.CHECK_VERSION: u'Номер версии',
    PromoCondition.CHECK_GEO_PUSH: u'Клиент активировал гео-пуш',
    PromoCondition.CHECK_VENUE: u'Заказ в кофейне',
    PromoCondition.CHECK_MARK: u'(метка) В заказе есть помеченные продукты',
    PromoCondition.CHECK_REPEATED_ORDER_BEFORE: u'Повторных заказов не было в течении N дней',
    PromoCondition.CHECK_MAX_USES: u'Максимальное кол-во использования акции на пользователя',
    PromoCondition.CHECK_MIN_DATE: u'Дата не ранее X',
    PromoCondition.CHECK_MAX_DATE: u'Дата не позднее X',
    PromoCondition.CHECK_LEFT_BASKET_PROMO: u'Клиент ушел из корзины',
    PromoCondition.CHECK_USER_INVITED: u'Пользователь пригласил другого',
    PromoCondition.CHECK_INVITED_USER: u'Пользователь был приглашен',
    PromoCondition.CHECK_DISH_HAS_GROUP_MODIFIERS: u'(метка) Пометить блюда с данным модификатором',
    PromoCondition.CHECK_DISH_HAS_NO_GROUP_MODIFIERS: u'(метка) Пометить блюда без данного модификатора',
    PromoCondition.CHECK_IS_NOT_DELIVERY_ZONE: u'Не зона доставки',
    PromoCondition.CHECK_IS_DELIVERY_ZONE: u'Зона доставки',
    PromoCondition.CHECK_REGISTRATION_DATE: u'Зарегистрировался больше N дней назад'
}

OUTCOME_MAP = {
    PromoOutcome.CASH_BACK: u"Кэшбек",
    PromoOutcome.DISCOUNT: u"Скидка",
    PromoOutcome.DISCOUNT_RICHEST: u'Скидка на самый дорогой продукт в заказе',
    PromoOutcome.DISCOUNT_CHEAPEST: u'Скидка на самый дешевый продукт в заказе',
    PromoOutcome.ACCUMULATE_GIFT_POINT: u'Баллы за продукты',
    PromoOutcome.ORDER_GIFT: u'Подарок',
    PromoOutcome.ORDER_ACCUMULATE_GIFT_POINT: u'Баллы за заказ',
    PromoOutcome.FIX_DISCOUNT: u'Фиксированная скидка',
    PromoOutcome.DELIVERY_SUM_DISCOUNT: u'Скидка на цену доставки',
    PromoOutcome.DELIVERY_FIX_SUM_DISCOUNT: u'Фиксированная скидка на цену доставки',
    PromoOutcome.PERCENT_GIFT_POINT: u'Баллы, равные проценту от суммы',
    PromoOutcome.SET_PERSISTENT_MARK: u'(метка) Запомнить метку',
    PromoOutcome.REMOVE_PERSISTENT_MARK: u'(метка) Удалить метку',
    PromoOutcome.MARKED_ORDER_GIFT: u'(метка) Подарить помеченные продукты',
    PromoOutcome.EMPTY: u'Выводить сообщение',
    PromoOutcome.CASH_ACCUMULATE_GIFT_POINT: u'Баллы за каждые N у.е в заказе',
    PromoOutcome.FORBID_MENU_ITEM: u'Запрет на продукт',
    PromoOutcome.FORBID_MENU_CATEGORY: u'Запрет на категорию',
    PromoOutcome.MARKED_DISCOUNT_CHEAPEST: u'(метка) Скидка на самый дешевый помеченный продукт',
    PromoOutcome.DELIVERY_MESSAGE: u'Сообщение о доставке',
    PromoOutcome.FIX_CASH_BACK: u'Фиксированный кэшбек',
    PromoOutcome.MARKED_DISCOUNT: u'(метка) Скидка на все помеченные продукты',
    PromoOutcome.MARKED_ACCUMULATE_GIFT_POINT: u'(метка) Баллы за каждый помеченный продукт',
    PromoOutcome.MARKED_FIX_DISCOUNT_CHEAPEST: u'(метка) Фиксированная скидка на самый дешевый помеченный продукт',
    PromoOutcome.FORBID_ORDER: u'Запрет на заказ'
}
