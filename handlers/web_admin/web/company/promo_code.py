# coding=utf-8
from datetime import datetime
from methods.auth import company_user_required
from base import CompanyBaseHandler
from methods.rendering import STR_DATETIME_FORMAT, HTML_STR_TIME_FORMAT
from models.promo_code import PromoCode, PROMO_CODE_KIND_MAP, PROMO_CODE_KIND_ADMIN, PromoCodeGroup, \
    PROMO_CODE_STATUS_MAP, KIND_WALLET, PromoCodePerforming

__author__ = 'dvpermyakov'


class ListPromoCodeHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        codes = PromoCode.query().fetch()
        self.render('/promo_code/list.html', promo_codes=codes, PROMO_CODE_KIND_MAP=PROMO_CODE_KIND_MAP,
                    PROMO_CODE_STATUS_MAP=PROMO_CODE_STATUS_MAP)


class ActivationsPromoCodeHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        key = self.request.get('key')
        promo_code = PromoCode.get_by_id(key)
        if not promo_code:
            self.abort(400)
        activations = PromoCodePerforming.query(PromoCodePerforming.promo_code == promo_code.key).fetch()
        for activation in activations:
            activation.client_obj = activation.client.get()
        self.render('/promo_code/activations.html', activations=activations)


class AddPromoCodeHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        kinds = []
        for kind in PROMO_CODE_KIND_ADMIN:
            kinds.append({
                'name': PROMO_CODE_KIND_MAP[kind],
                'value': kind
            })
        self.render('/promo_code/add.html', kinds=kinds)

    @company_user_required
    def post(self):
        kind = self.request.get_range('kind')
        value = self.request.get_range('value')
        amount = self.request.get_range('amount')
        max_activations = self.request.get_range('max_activations')
        title = self.request.get('title')
        message = self.request.get('message')
        group = PromoCodeGroup()
        group.put()
        for number in xrange(amount):
            promo_code = PromoCode.create(group, kind, max_activations, message=message, title=title, value=value)
            group.promo_codes.append(promo_code.key)
        group.put()
        self.redirect('/company/promo_code/list')