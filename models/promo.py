# coding=utf-8
import random
from google.appengine.ext import ndb
from methods import fastcounter
from models import STATUS_AVAILABLE, STATUS_UNAVAILABLE, GroupModifier, STATUS_CHOICES
from models.menu import MenuItem, SingleModifier
from models.schedule import Schedule

__author__ = 'dvpermyakov'


class GiftMenuItem(ndb.Model):   # self.key.id() == item.key.id()
    item = ndb.KeyProperty(kind=MenuItem, required=True)
    status = ndb.IntegerProperty(choices=[STATUS_AVAILABLE, STATUS_UNAVAILABLE], default=STATUS_AVAILABLE)
    promo_id = ndb.IntegerProperty(required=True)  # it relates to empatika-promos
    points = ndb.IntegerProperty(required=True)  # how many spent
    additional_group_choice_restrictions = ndb.IntegerProperty(repeated=True)

    def dict(self):
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
            result['title'] = u'%s %s' % (item.title, u','.join([GroupModifier.get_modifier_by_choice(choice).get_choice_by_id(choice).title for choice in self.additional_group_choice_restrictions]))
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
    CHOICES = (DISCOUNT, CASH_BACK, DISCOUNT_CHEAPEST, DISCOUNT_RICHEST, ACCUMULATE_GIFT_POINT, ORDER_GIFT,
               ORDER_ACCUMULATE_GIFT_POINT, FIX_DISCOUNT, DELIVERY_SUM_DISCOUNT, DELIVERY_FIX_SUM_DISCOUNT,
               PERCENT_GIFT_POINT, SET_PERSISTENT_MARK, REMOVE_PERSISTENT_MARK, MARKED_ORDER_GIFT, EMPTY,
               CASH_ACCUMULATE_GIFT_POINT, FORBID_MENU_ITEM, MARKED_DISCOUNT_CHEAPEST)

    item_details = ndb.LocalStructuredProperty(PromoMenuItem)
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
    CHOICES = (CHECK_TYPE_DELIVERY, CHECK_FIRST_ORDER, CHECK_MAX_ORDER_SUM, CHECK_ITEM_IN_ORDER, CHECK_REPEATED_ORDERS,
               CHECK_MIN_ORDER_SUM, CHECK_HAPPY_HOURS, CHECK_MIN_ORDER_SUM_WITH_PROMOS, CHECK_GROUP_MODIFIER_CHOICE,
               CHECK_NOT_GROUP_MODIFIER_CHOICE, CHECK_PAYMENT_TYPE, CHECK_HAPPY_HOURS_CREATED_TIME,
               MARK_ITEM_WITH_CATEGORY, MARK_ITEM_WITHOUT_CATEGORY, CHECK_MARKED_MIN_SUM, MARK_ITEM, MARK_NOT_ITEM,
               MARK_ITEM_WITH_QUANTITY, CHECK_PROMO_CODE, CHECK_ORDER_NUMBER, CHECK_ITEM_NOT_IN_ORDER,
               CHECK_MARKED_QUANTITY)

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

    conflicts = ndb.KeyProperty(repeated=True)  # kind=Promo  # Not Implemented
    priority = ndb.IntegerProperty()
    more_one = ndb.BooleanProperty(default=True)              # Not Implemented
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    visible = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    @classmethod
    def query_promos(cls, *args, **kwargs):  # AUTO_APP = 0
        from models.config.config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.promo import get_promos
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
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

    def dict(self, hostname):
        icon = None
        if self.outcomes:
            outcome = self.outcomes[0]
            if outcome.method in [PromoOutcome.ACCUMULATE_GIFT_POINT, PromoOutcome.ORDER_ACCUMULATE_GIFT_POINT]:
                icon = self._get_url(hostname, self.BONUS_ICON)
            elif outcome.method in [PromoOutcome.CASH_BACK]:
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
    PromoCondition.CHECK_HAPPY_HOURS: u'Счастливые часы время заказа',
    PromoCondition.CHECK_MIN_ORDER_SUM_WITH_PROMOS: u'Минимальная сумма с учетом акций',
    PromoCondition.CHECK_GROUP_MODIFIER_CHOICE: u'Выбор группового модификатора в заказе',
    PromoCondition.CHECK_NOT_GROUP_MODIFIER_CHOICE: u'Выбора группового модификатора нет в заказе',
    PromoCondition.CHECK_PAYMENT_TYPE: u'Тип оплаты',
    PromoCondition.CHECK_HAPPY_HOURS_CREATED_TIME: u'Счастливые часы время создания заказа',
    PromoCondition.MARK_ITEM_WITH_CATEGORY: u'Продукты из категории (метка)',
    PromoCondition.MARK_ITEM_WITHOUT_CATEGORY: u'Продукты не из категории (метка)',
    PromoCondition.CHECK_MARKED_MIN_SUM: u'Минимальная сумма помеченных продуктов',
    PromoCondition.MARK_ITEM: u'Продукт (метка)',
    PromoCondition.MARK_NOT_ITEM: u'Не продукт (метка)',
    PromoCondition.MARK_ITEM_WITH_QUANTITY: u'Минимальное кол-во помеченных продуктов каждого типа (метка)',
    PromoCondition.CHECK_PROMO_CODE: u'Клиент активировал промо-код из группы',
    PromoCondition.CHECK_ORDER_NUMBER: u'Кратный N заказ клиента',
    PromoCondition.CHECK_ITEM_NOT_IN_ORDER: u'Продукта нет в заказе',
    PromoCondition.CHECK_MARKED_QUANTITY: u'Минимальное кол-во помеченных продуктов (метка)'
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
    PromoOutcome.SET_PERSISTENT_MARK: u'Установить метку (метка)',
    PromoOutcome.REMOVE_PERSISTENT_MARK: u'Удалить метку (метка)',
    PromoOutcome.MARKED_ORDER_GIFT: u'Подарить помеченные продукты (метка)',
    PromoOutcome.EMPTY: u'Выводить сообщение',
    PromoOutcome.CASH_ACCUMULATE_GIFT_POINT: u'Баллы за каждые N у.е в заказе',
    PromoOutcome.FORBID_MENU_ITEM: u'Запрет на продукт',
    PromoOutcome.MARKED_DISCOUNT_CHEAPEST: u'Скидка на самый дешевый продукт в заказе (метка)'
}