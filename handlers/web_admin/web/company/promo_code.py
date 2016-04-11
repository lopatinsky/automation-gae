# coding=utf-8
from methods.auth import promo_code_rights_required
from base import CompanyBaseHandler
from models.promo_code import PromoCode, PROMO_CODE_KIND_MAP, PROMO_CODE_KIND_ADMIN, PromoCodeGroup, \
    PROMO_CODE_STATUS_MAP, PromoCodePerforming, KIND_SHARE_INVITATION

__author__ = 'dvpermyakov'


class ListPromoCodeHandler(CompanyBaseHandler):
    @promo_code_rights_required
    def get(self):
        codes = PromoCode.query(PromoCode.kind != KIND_SHARE_INVITATION).fetch()
        for code in codes:
            code.promo_code_key = code.key.id().decode('utf-8')
        self.render('/promo_code/list.html', promo_codes=codes, PROMO_CODE_KIND_MAP=PROMO_CODE_KIND_MAP,
                    PROMO_CODE_STATUS_MAP=PROMO_CODE_STATUS_MAP)


class ActivationsPromoCodeHandler(CompanyBaseHandler):
    @promo_code_rights_required
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
    @promo_code_rights_required
    def get(self):
        kinds = []
        for kind in PROMO_CODE_KIND_ADMIN:
            kinds.append({
                'name': PROMO_CODE_KIND_MAP[kind],
                'value': kind
            })
        self.render('/promo_code/add.html', kinds=kinds)

    @promo_code_rights_required
    def post(self):
        key = self.request.get('key')
        kind = self.request.get_range('kind')
        value = self.request.get_range('value')
        amount = self.request.get_range('amount')
        max_activations = self.request.get_range('max_activations')
        title = self.request.get('title')
        message = self.request.get('message')
        persist = bool(self.request.get('persist'))
        group = PromoCodeGroup()
        group.put()
        for number in xrange(amount):
            promo_code = PromoCode.create(group, kind, max_activations, message=message, title=title, value=value,
                                          promo_code_key=key, persist=persist)
            group.promo_codes.append(promo_code.key)
        group.put()
        self.redirect('/company/promo_code/list')