# -*- coding: utf-8 -*-
import random

__author__ = 'dvpermyakov'

from base import ApiHandler
from methods import branch_io, alfa_bank, twilio
from models import Share, Client, SharedFreeCup, PaymentType, STATUS_AVAILABLE, CARD_PAYMENT_TYPE, BONUS_PAYMENT_TYPE


TEXTS = [
    ("a", u"Заказываю кофе через приложение Даблби. Экспертам хорошего кофе каждая шестая кружка в подарок. Вот как "
          u"сейчас."),
    ("b", u"Кофе встроился в мой метаболизм. Если у тебя то же самое, скачай приложение Даблби и получай каждую "
          u"шестую доз... кружку в подарок"),
    ("c", u"Этот колумбийский кофе вштыривает как надо, бро. Скачай приложение Даблби и получай качественный кофе "
          u"в подарок"),
]
random.seed()


class GetSharedInfo(ApiHandler):
    def get(self):
        text_id, text = random.choice(TEXTS)

        url_template = "http://dblb.mobi/get/%%s%s%s"
        ua = self.request.headers["User-Agent"]
        platform_part = "a" if "Android" in ua else "i"
        client_id = self.request.get("client_id")
        client_id_part = "" if not client_id else ("/" + client_id)
        campaign_url_template = url_template % (platform_part, client_id_part)

        self.render_json({
            'image_url': 'http://empatika-doubleb-test.appspot.com/images/shared_image.png',
            'fb_android_image_url': 'http://empatika-doubleb-test.appspot.com/images/facebook_shared_image.png',
            'text_share_new_order': text,
            'text_share_about_app': "Советую попробовать это интересное приложение для заказа кофе в 3 клика:",
            'app_url': campaign_url_template % text_id,
            'about_url': campaign_url_template % 'd',
            'screen_title': text,
            'screen_text': 'Расскажи друзьям, если тебе нравится приложение Даблби.'
        })


class PutBranchIoInfoHandler(ApiHandler):
    def post(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        share_id = self.request.get_range('share_id')
        share = Share.get_by_id(share_id)
        if not share:
            self.abort(400)
        if share.share_type == branch_io.INVITATION:
            SharedFreeCup(sender=share.sender, recipient=client.key).put()
            self.render_json({})
        elif share.share_type == branch_io.GIFT:
            pass
        else:
            pass


class GetInvitationUrlHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        channel = self.request.get_range('channel')
        if channel not in [branch_io.VK, branch_io.FACEBOOK, branch_io.SMS, branch_io.EMAIL, branch_io.OTHER]:
            self.abort(400)
        share = Share(share_type=branch_io.INVITATION, sender=client.key)
        share.put()
        url = branch_io.create_url(share.key.id(), branch_io.INVITATION, channel)

        self.render_json({
            'url': url
        })


class GetGiftUrlHandler(ApiHandler):
    FIX_GIFT_SUM = 300

    def send_error(self, error):
        self.response.set_status(400)
        self.render_json({
            'error': True,
            'description': error
        })

    def success(self, sender, phone, channel):
        share = Share(share_type=branch_io.GIFT, sender=sender.key)
        share.put()
        url = branch_io.create_url(share.key.id(), branch_io.INVITATION, channel)
        #twilio.send_sms([phone], u'Получай свою кружку в подарок %s' % url)
        self.render_json({
            'success': True,
            'url': url
        })

    def post(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        recipient_phone = self.request.get('recipient_phone')
        channel = self.request.get_range('channel')
        if channel not in [branch_io.VK, branch_io.FACEBOOK, branch_io.SMS, branch_io.EMAIL, branch_io.OTHER]:
            self.abort(400)
        order_id = self.request.get_range('order_id')
        payment_type_id = self.request.get('payment_type_id')
        payment_type = PaymentType.get_by_id(payment_type_id)
        if payment_type.status == STATUS_AVAILABLE:
            if payment_type_id == CARD_PAYMENT_TYPE:
                alpha_client_id = self.request.get('alpha_client_id')
                binding_id = self.request.get('binding_id')
                return_url = self.request.get('return_utl')
                mastercard = self.request.get('mastercard')

                success, error = alfa_bank.create_simple(self.FIX_GIFT_SUM, order_id, return_url, alpha_client_id)
                if success:
                    success, error = alfa_bank.hold_and_check(payment_type_id, binding_id)
                if not success:
                    self.send_error(error)
                else:
                    self.success(client, recipient_phone, channel)

            elif payment_type_id == BONUS_PAYMENT_TYPE:
                pass
        else:
            self.send_error(u'Данный вид оплаты недоступен')