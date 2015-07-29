# coding: utf-8
import json
from models.promo_code import PromoCode, KIND_SHARE_GIFT, PromoCodeGroup

__author__ = 'dvpermyakov'

import time
from models.payment_types import CARD_PAYMENT_TYPE
from base import ApiHandler
from methods import branch_io, alfa_bank
from models import Share, Client, PaymentType, STATUS_AVAILABLE, SharedGift
from models.share import SharedGiftMenuItem
import logging


class GetShareUrlHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        share = Share.query(Share.sender == client.key, Share.status == Share.ACTIVE,
                            Share.share_type == branch_io.SHARE).get()
        if not share:
            share = Share(share_type=branch_io.SHARE, sender=client.key)
            share.put()  # need share id

            if 'iOS' in self.request.headers["User-Agent"]:
                user_agent = 'ios'
            elif 'Android' in self.request.headers["User-Agent"]:
                user_agent = 'android'
            else:
                user_agent = 'unknown'
            urls = [{
                'url': branch_io.create_url(share.key.id(), branch_io.SHARE, channel, user_agent),
                'channel': channel
            } for channel in branch_io.CHANNELS]
            share.urls = [url['url'] for url in urls]
            share.put()

        self.render_json({})  # todo: need to update


class GetInvitationUrlHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        share = Share.query(Share.sender == client.key, Share.status == Share.ACTIVE,
                            Share.share_type == branch_io.INVITATION).get()
        if not share:
            share = Share(share_type=branch_io.INVITATION, sender=client.key)
            share.put()  # need share id

            if 'iOS' in self.request.headers["User-Agent"]:
                user_agent = 'ios'
            elif 'Android' in self.request.headers["User-Agent"]:
                user_agent = 'android'
            else:
                user_agent = 'unknown'
            urls = [{
                'url': branch_io.create_url(share.key.id(), branch_io.INVITATION, channel, user_agent),
                'channel': channel
            } for channel in branch_io.CHANNELS]
            share.urls = [url['url'] for url in urls]
            share.put()

        # todo: need to update
        self.render_json({
            'urls': share.urls
        })


class GetGiftUrlHandler(ApiHandler):
    def send_error(self, error):
        logging.info(error)
        self.response.set_status(400)
        self.render_json({
            'success': False,
            'description': error
        })

    def success(self, sender, gift, promo_code, name=None, phone=None):
        share = Share(share_type=branch_io.GIFT, sender=sender.key)
        share.put()
        if 'iOS' in self.request.headers["User-Agent"]:
            user_agent = 'ios'
        elif 'Android' in self.request.headers["User-Agent"]:
            user_agent = 'android'
        else:
            user_agent = 'unknown'
        recipient = {
            'name': name,
            'phone': phone
        }
        url = branch_io.create_url(share.key.id(), branch_io.INVITATION, branch_io.SMS, user_agent, recipient=recipient)
        share.urls = [url]
        share.put()
        gift.share_id = share.key.id()
        gift.put()
        self.render_json({
            'success': True,
            'sms_text': u'ссылка = %s, код = %s' % (url, promo_code.key.id())
        })

    def post(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        items_json = json.loads(self.request.get('items'))
        item_id = int(items_json[0]['item_id'])
        share_item = SharedGiftMenuItem.get_by_id(item_id)
        if not share_item:
            self.abort(400)
        item = share_item.item.get()
        total_sum = self.request.get('total_sum')
        if float(total_sum) != item.float_price:
            return self.send_error(u'Сумма была пересчитана')
        recipient_phone = "".join(c for c in self.request.get('recipient_phone') if '0' <= c <= '9')
        recipient_name = self.request.get('recipient_name')
        payment_type_id = self.request.get_range('payment_type_id')
        payment_type = PaymentType.get_by_id(str(payment_type_id))
        if payment_type.status == STATUS_AVAILABLE:
            if payment_type_id == CARD_PAYMENT_TYPE:
                alpha_client_id = self.request.get('alpha_client_id')
                binding_id = self.request.get('binding_id')
                return_url = self.request.get('return_url')

                order_id = "gift_%s_%s" % (client_id, int(time.time()))
                success, result = alfa_bank.create_simple(int(item.float_price * 100), order_id, return_url, alpha_client_id)
                if success:
                    success, error = alfa_bank.hold_and_check(result, binding_id)
                else:
                    error = result
                if not success:
                    self.send_error(error)
                else:
                    group_promo_codes = PromoCodeGroup()
                    group_promo_codes.put()
                    promo_code = PromoCode.create(group_promo_codes, KIND_SHARE_GIFT, 1)
                    promo_code.put()
                    group_promo_codes.promo_codes = [promo_code.key]
                    group_promo_codes.put()
                    gift = SharedGift(client_id=client_id, total_sum=item.float_price, order_id=order_id,
                                      payment_type_id=payment_type_id, payment_id=result, share_item=share_item.key,
                                      recipient_name=recipient_name, recipient_phone=recipient_phone,
                                      promo_code=promo_code.key)
                    self.success(client, gift=gift, promo_code=promo_code, name=recipient_name, phone=recipient_phone)
            else:
                self.send_error(u'Возможна оплата только картой')
        else:
            self.send_error(u'Данный вид оплаты недоступен')