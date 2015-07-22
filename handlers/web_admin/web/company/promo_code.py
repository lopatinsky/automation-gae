from datetime import datetime
from methods.auth import company_user_required
from base import CompanyBaseHandler
from methods.rendering import STR_DATETIME_FORMAT
from models.promo_code import PromoCode, PROMO_CODE_KIND_MAP

__author__ = 'dvpermyakov'


class ListPromoCodeHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        codes = PromoCode.query().fetch()
        for code in codes:
            code.start_str = datetime.strftime(code.start, STR_DATETIME_FORMAT)
            code.end_str = datetime.strftime(code.end, STR_DATETIME_FORMAT)
        self.render('/promo_code/list.html', codes=codes, PROMO_CODE_KIND_MAP=PROMO_CODE_KIND_MAP)


class AddPromoCodeHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        pass

    @company_user_required
    def post(self):
        pass