# coding=utf-8
from datetime import datetime
from methods.auth import company_user_required
from base import CompanyBaseHandler
from methods.rendering import STR_DATETIME_FORMAT, HTML_STR_TIME_FORMAT
from models.promo_code import PromoCode, PROMO_CODE_KIND_MAP, PROMO_CODE_KIND_ADMIN, PromoCodeGroup, \
    PROMO_CODE_STATUS_MAP, KIND_WALLET, PromoCodeDeposit

__author__ = 'dvpermyakov'


class ListPromoCodeHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        codes = PromoCode.query().fetch()
        for code in codes:
            code.start_str = datetime.strftime(code.start, STR_DATETIME_FORMAT)
            code.end_str = datetime.strftime(code.end, STR_DATETIME_FORMAT)
        self.render('/promo_code/list.html', promo_codes=codes, PROMO_CODE_KIND_MAP=PROMO_CODE_KIND_MAP,
                    PROMO_CODE_STATUS_MAP=PROMO_CODE_STATUS_MAP)


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
        value = self.request.get_range('number')
        amount = self.request.get_range('amount')
        max_activations = self.request.get_range('max_activations')
        title = self.request.get('title')
        one_client = bool(self.request.get('one_client'))
        start = self.request.get('start')
        end = self.request.get('end')
        if start:
            try:
                start = datetime.strptime(start, HTML_STR_TIME_FORMAT)
            except:
                return error(u'Неверное время начала')
        else:
            return error(u'Введите время начала')
        if end:
            try:
                end = datetime.strptime(end, HTML_STR_TIME_FORMAT)
            except:
                return error(u'Неверное время начала')
        else:
            return error(u'Введите время начала')
        group = PromoCodeGroup()
        for number in xrange(amount):
            promo_code = PromoCode.create(start, end, kind, max_activations, one_client, title=title)
            if promo_code.kind == KIND_WALLET:
                PromoCodeDeposit(promo_code=promo_code.key, amount=value).put()
            group.promo_codes.append(promo_code.key)
        group.put()
        self.redirect('/company/promo_code/list')