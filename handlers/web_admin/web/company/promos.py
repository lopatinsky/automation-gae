# coding:utf-8
from methods.auth import company_user_required
from models import Promo, PromoCondition, PromoOutcome, IN_CAFE, SELF
from base import CompanyBaseHandler

__author__ = 'dvpermyakov'

CONDITION_MAP = {
    PromoCondition.CHECK_FIRST_ORDER: u"Первый заказ",
    PromoCondition.CHECK_TYPE_DELIVERY: u"Тип доставки"
}

OUTCOME_MAP = {
    PromoOutcome.CASH_BACK: u"Кэшбек",
    PromoOutcome.DISCOUNT: u"Скидка"
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