# coding=utf-8
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.api.urlfetch_errors import DeadlineExceededError
from models import Client, SharedGift
from models.promo_code import PromoCode, KIND_SHARE_GIFT, STATUS_ACTIVE, KIND_WALLET, PromoCodeDeposit, \
    PromoCodePerforming

__author__ = 'dvpermyakov'

from base import ApiHandler


class EnterPromoCode(ApiHandler):
    def send_error(self, description):
        return self.render_json({
            'success': False,
            'description': description
        })

    def send_success(self, promo_code):
        return self.render_json({
            'success': True,
            'message': promo_code.message,
        })

    def post(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        key = self.request.get('key')
        if not key:
            return self.send_error(u'Введите ключ')
        promo_code = PromoCode.get_by_id(key)
        if promo_code:
            if promo_code.status == STATUS_ACTIVE:
                if promo_code.kind == KIND_SHARE_GIFT:
                    gift = SharedGift.query(SharedGift.promo_code == promo_code.key).get()
                    if gift.status == SharedGift.READY:
                        gift.deactivate(client, namespace_manager.get_namespace())
                        return self.send_success(promo_code)
                elif promo_code.kind == KIND_WALLET:
                    try:
                        deposit = PromoCodeDeposit.query(PromoCodeDeposit.promo_code == promo_code.key).get()
                        if deposit:
                            deposit.deposit(client)
                            return self.send_success(promo_code)
                    except DeadlineExceededError:
                        return self.send_error(u'Пожалуйста, повторите попытку...')
            else:
                return self.send_error(u'Промо код не активен')
        else:
            return self.send_error(u'Промо код не найден')


class PromoCodeHistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        self.render_json({
            'activation': [performing.promo_code.get().dict() for performing in PromoCodePerforming.query(PromoCodePerforming.client == client.key).fetch()]
        })