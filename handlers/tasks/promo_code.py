import logging
from webapp2 import RequestHandler
from models.promo_code import PromoCode, STATUS_CREATED

__author__ = 'dvpermyakov'


class StartPromoCodeHandler(RequestHandler):
    def post(self):
        code_id = self.request.get('code_id')
        logging.info(code_id)
        promo_code = PromoCode.get_by_id(code_id)
        if not promo_code:
            self.abort(400)
        if promo_code.status == STATUS_CREATED:
            promo_code.activate()


class ClosePromoCodeHandler(RequestHandler):
    def post(self):
        code_id = self.request.get('code_id')
        promo_code = PromoCode.get_by_id(code_id)
        if not promo_code:
            self.abort(400)
        promo_code.deactivate()