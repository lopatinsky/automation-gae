# -*- coding: utf-8 -*-
import random
import time

__author__ = 'dvpermyakov'

from base import ApiHandler
from methods import branch_io, alfa_bank
from models import Share, Client, PaymentType, STATUS_AVAILABLE, CARD_PAYMENT_TYPE, Order, SharedGift
import logging


TEXTS = [
    ("a", u"Заказываю кофе через приложение Даблби. Экспертам хорошего кофе каждая шестая кружка в подарок. Вот как "
          u"сейчас."),
    ("b", u"Кофе встроился в мой метаболизм. Если у тебя то же самое, скачай приложение Даблби и получай каждую "
          u"шестую доз... кружку в подарок"),
    ("c", u"Этот колумбийский кофе вштыривает как надо, бро. Скачай приложение Даблби и получай качественный кофе "
          u"в подарок"),
]
random.seed()


def get_general_shared_dict():
    text_id, text = random.choice(TEXTS)
    return text_id, {
        'image_url': 'http://empatika-doubleb-test.appspot.com/images/shared_image.png',
        'fb_android_image_url': 'http://empatika-doubleb-test.appspot.com/images/facebook_shared_image.png',
        'text_share_new_order': text,
        'text_share_about_app': "Советую попробовать это интересное приложение для заказа кофе в 3 клика:",
        'screen_title': text,
        'screen_text': 'Расскажи друзьям, если тебе нравится приложение Даблби.'
    }


class GetPreText(ApiHandler):
    def get(self):
        self.render_json({
            'head': 'Подари кофе другу',
            'text': (u'Вы можете подарить напиток своему другу!\n'
                    u'Для этого введите его имя и телефон.\n'
                    u'С вашей карты спишется 350 рублей, '
                    u'которые ваш друг сможет потратить на любой напиток в кофейне Даблби.')
        })


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


class GetInvitationUrlHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        share = Share(share_type=branch_io.INVITATION, sender=client.key)
        share.put()

        text_id, values = get_general_shared_dict()

        if 'iOS' in self.request.headers["User-Agent"]:
            user_agent = 'ios'
        elif 'Android' in self.request.headers["User-Agent"]:
            user_agent = 'android'
        else:
            user_agent = 'unknown'
        urls = [{
            'url': branch_io.create_url(share.key.id(), branch_io.INVITATION, channel, user_agent,
                                        custom_tags={"text_id": text_id}),
            'channel': channel
        } for channel in branch_io.CHANNELS]
        share.urls = [url['url'] for url in urls]
        share.put()

        values['urls'] = urls

        self.render_json(values)


class GetGiftUrlHandler(ApiHandler):
    FIX_GIFT_SUM = 350

    def send_error(self, error):
        logging.info(error)

        self.response.set_status(400)
        self.render_json({
            'success': False,
            'description': error
        })

    def success(self, sender, gift, name=None, phone=None):
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
            'text': (u'%s %s подарил вам кружку кофе. '
                     u'Получить ее вы сможете, пройдя по %s и установив приложение сети кофеен Даблби. '
                     u'Закажите любой напиток, расплатитесь подарочной кружкой и насладитесь отличным кофе.'
                     % (sender.name, sender.surname, url))
        })

    def post(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
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
                success, result = alfa_bank.create_simple(self.FIX_GIFT_SUM, order_id, return_url, alpha_client_id)
                if success:
                    success, error = alfa_bank.hold_and_check(result, binding_id)
                else:
                    error = result
                if not success:
                    self.send_error(error)
                else:
                    gift = SharedGift(client_id=client_id, total_sum=self.FIX_GIFT_SUM, order_id=order_id,
                                      payment_type_id=payment_type_id, payment_id=result)
                    self.success(client, gift=gift, name=recipient_name, phone=recipient_phone)
            else:
                self.send_error(u'Возможна оплата только картой')
        else:
            self.send_error(u'Данный вид оплаты недоступен')