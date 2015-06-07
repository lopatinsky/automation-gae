# coding:utf-8
from methods.auth import company_user_required
from models import Promo, PromoCondition, PromoOutcome, IN_CAFE, SELF, STATUS_UNAVAILABLE, STATUS_AVAILABLE
from base import CompanyBaseHandler

__author__ = 'dvpermyakov'

CONDITION_MAP = {
    PromoCondition.CHECK_FIRST_ORDER: u"Первый заказ",
    PromoCondition.CHECK_TYPE_DELIVERY: u"Тип доставки",
    PromoCondition.CHECK_MAX_ORDER_SUM: u'Максимальная сумма',
    PromoCondition.CHECK_ITEM_IN_ORDER: u'Продукт в заказе',
    PromoCondition.CHECK_REPEATED_ORDERS: u'Повторный заказ'
}

OUTCOME_MAP = {
    PromoOutcome.CASH_BACK: u"Кэшбек",
    PromoOutcome.DISCOUNT: u"Скидка",
    PromoOutcome.DISCOUNT_RICHEST: u'Скидка на самый дорогой продукт в заказе',
    PromoOutcome.DISCOUNT_CHEAPEST: u'Скидка на самый дешевый продукт в заказе',
    PromoOutcome.ACCUMULATE_GIFT_POINT: u'Баллы',
    PromoOutcome.ORDER_GIFT: u'Подарок',
    PromoOutcome.ORDER_ACCUMULATE_GIFT_POINT: u'Баллы за заказ'
}

DELIVERY_MAP = {
    IN_CAFE: u"В кафе",
    SELF: u"С собой"
}


class PromoListHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        promos = Promo.query().fetch()
        for promo in promos:
            for condition in promo.conditions:
                condition.value_string = str(condition.value) if condition.value else ""
                if condition.method == PromoCondition.CHECK_TYPE_DELIVERY:
                    condition.value_string = DELIVERY_MAP[condition.value]

        self.render('/promos/list.html',
                    promos=promos,
                    condition_map=CONDITION_MAP,
                    outcome_map=OUTCOME_MAP)

    def post(self):
        for promo in Promo.query().fetch():
            confirmed = bool(self.request.get(str(promo.key.id())))
            if confirmed:
                promo.status = STATUS_AVAILABLE
            else:
                promo.status = STATUS_UNAVAILABLE
            promo.put()
        self.redirect('/company/main')


class AddPromoHandler(CompanyBaseHandler):
    def get(self):
        pass


class ConditionChooseMenuItemHandler(CompanyBaseHandler):
    def get(self):
        pass


class OutcomeChooseMenuItemHandler(CompanyBaseHandler):
    def get(self):
        pass