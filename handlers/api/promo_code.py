# coding=utf-8
from models import Client
from models.promo_code import PromoCode, PromoCodePerforming
import logging

__author__ = 'dvpermyakov'

from base import ApiHandler


class EnterPromoCode(ApiHandler):
    def send_error(self, description):
        logging.info('error = %s' % description)
        return self.render_json({
            'success': False,
            'description': description
        })

    def send_success(self, promo_code):
        logging.info('message = %s' % promo_code.message)
        return self.render_json({
            'success': True,
            'message': promo_code.message,
        })

    def post(self):
        client_id = self.request.get_range('client_id') or int(self.request.headers.get('Client-Id') or 0)
        client = Client.get(client_id)
        if not client:
            self.abort(400)
        key = self.request.get('key')
        if not key:
            return self.send_error(u'Введите ключ')
        promo_code = PromoCode.get_by_id(key)
        if promo_code:
            success, description = promo_code.check(client)
            if success:
                promo_code.perform(client)
                return self.send_success(promo_code)
            else:
                return self.send_error(description)
        else:
            return self.send_error(u'Промо код не найден')


class PromoCodeHistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id') or int(self.request.headers.get('Client-Id') or 0)
        client = Client.get(client_id)
        if not client:
            self.abort(400)
        self.render_json({
            'history': [performing.promo_code.get().dict() for performing in PromoCodePerforming.query(PromoCodePerforming.client == client.key).fetch()]
        })