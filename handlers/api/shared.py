# coding: utf-8
import json

from google.appengine.ext.deferred import deferred

from models.config.config import EMAIL_FROM, Config
from methods.emails.mandrill import send_email
from methods.orders.validation.validation import set_modifiers, set_price_with_modifiers
from methods.sms.sms_pilot import send_sms
from models.legal import LegalInfo
from models.promo_code import PromoCode, KIND_SHARE_GIFT, PromoCodeGroup, KIND_SHARE_INVITATION

__author__ = 'dvpermyakov'

import time
from models.payment_types import CARD_PAYMENT_TYPE
from base import ApiHandler
from methods import branch_io, alfa_bank
from models import Share, Client, PaymentType, STATUS_AVAILABLE, SharedGift, STATUS_UNAVAILABLE
from models.share import SharedGiftMenuItem, ChosenSharedGiftMenuItem, ChannelUrl
from methods.rendering import get_phone
import logging


class GetInvitationInfoHandler(ApiHandler):
    def get(self):
        config = Config.get()
        if not config.SHARE_INVITATION_ENABLED:
            self.abort(403)
        self.render_json({
            'title': config.SHARE_INVITATION_MODULE.about_title,
            'description': config.SHARE_INVITATION_MODULE.about_description
        })


class GetInvitationUrlHandler(ApiHandler):
    def get(self):
        client_id = int(self.request.headers.get('Client-Id') or 0)
        if not client_id:
            self.abort(400)
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)

        config = Config.get()
        if not config.SHARE_INVITATION_ENABLED:
            self.abort(403)
        share = Share.query(Share.sender == client.key, Share.status == Share.ACTIVE,
                            Share.share_type == branch_io.INVITATION).get()
        logging.info('Found share: %s' % share)
        if share and not share.promo_code and not share.channel_urls:
            self.abort(412)
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
            share.channel_urls = [ChannelUrl(url=url['url'], channel=url['channel']) for url in urls]
            group_promo_codes = PromoCodeGroup()
            group_promo_codes.put()
            promo_code = PromoCode.create(group_promo_codes, KIND_SHARE_INVITATION, 100000)
            share.promo_code = promo_code.key
            share.put()

        self.render_json({
            'text': config.SHARE_INVITATION_MODULE.invitation_text,
            'urls': [channel_url.dict() for channel_url in share.channel_urls],
            'image': config.SHARE_INVITATION_MODULE.invitation_image,
            'promo_code': share.promo_code.id()
        })


class GetGiftUrlHandler(ApiHandler):
    def send_error(self, error):
        logging.info(error)
        self.response.set_status(400)
        self.render_json({
            'success': False,
            'description': error
        })

    def success(self, sender, gift, promo_code, sender_phone, sender_email, reciptient_name, recipient_phone):
        share = Share(share_type=branch_io.GIFT, sender=sender.key)
        share.put()
        if 'iOS' in self.request.headers["User-Agent"]:
            user_agent = 'ios'
        elif 'Android' in self.request.headers["User-Agent"]:
            user_agent = 'android'
        else:
            user_agent = 'unknown'
        recipient = {
            'name': reciptient_name,
            'phone': recipient_phone
        }
        url = branch_io.create_url(share.key.id(), branch_io.INVITATION, branch_io.SMS, user_agent, recipient=recipient)
        share.urls = [url]
        share.put()
        gift.share_id = share.key.id()
        gift.put()
        text = u'ссылка = %s, код = %s' % (url, promo_code.key.id())
        try:
            send_sms([sender_phone], text)
        except Exception as e:
            logging.warning(str(e))
        deferred.defer(send_email, EMAIL_FROM, sender_email, u'Подарок другу', text)
        self.render_json({
            'success': True,
            'sms_text': text
        })

    def post(self):
        client_id = self.request.get_range('client_id') or int(self.request.headers.get('Client-Id') or 0)
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        sender_phone = get_phone(self.request.get('sender_phone'))
        sender_email = self.request.get('sender_email')
        items_json = json.loads(self.request.get('items'))
        items = set_modifiers(items_json)
        items = set_price_with_modifiers(items)
        share_items = []
        for item in items:
            share_item = SharedGiftMenuItem.get_by_id(item.key.id())
            if share_item.status == STATUS_UNAVAILABLE:
                return self.send_error(u'Продукт %s недоступен' % item.title)
            chosen_shared_item = ChosenSharedGiftMenuItem(shared_item=share_item.key)
            chosen_shared_item.group_choice_ids = [modifier.choice.choice_id for modifier in item.chosen_group_modifiers]
            chosen_shared_item.single_modifiers = [modifier.key for modifier in item.chosen_single_modifiers]
            chosen_shared_item.put()
            share_items.append(chosen_shared_item)
        total_sum = 0.0
        for item in items:
            total_sum += item.total_price
        request_total_sum = float(self.request.get('total_sum'))
        if round(total_sum) != round(request_total_sum):
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
                legal = LegalInfo.query().get()  # TODO find solution for multiple legals
                success, result = alfa_bank.create_simple(legal.alfa_login, legal.alfa_password, int(total_sum * 100),
                                                          order_id, return_url, alpha_client_id)
                if success:
                    success, error = alfa_bank.hold_and_check(legal.alfa_login, legal.alfa_password, result, binding_id)
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
                    share_item_keys = [item.key for item in share_items]
                    gift = SharedGift(client_id=client_id, total_sum=total_sum, order_id=order_id,
                                      payment_type_id=payment_type_id, payment_id=result, share_items=share_item_keys,
                                      recipient_name=recipient_name, recipient_phone=recipient_phone,
                                      promo_code=promo_code.key)
                    self.success(client, gift, promo_code, sender_phone, sender_email, recipient_name, recipient_phone)
            else:
                self.send_error(u'Возможна оплата только картой')
        else:
            self.send_error(u'Данный вид оплаты недоступен')
