# coding: utf-8
from config import Config

__author__ = 'dvpermyakov'

import time
from models.payment_types import CARD_PAYMENT_TYPE
from base import ApiHandler
from methods import branch_io, alfa_bank
from models import Share, Client, PaymentType, STATUS_AVAILABLE, SharedGift, MenuItem
import logging


def get_general_shared_dict():
    config = Config.get()
    return {
        'image': config.SHARE_IMAGE_URL,
        'text': config.SHARE_TEXT
    }


class GetPreText(ApiHandler):  # todo: remove?
    def get(self):
        self.render_json({
            'head': 'Подари кофе другу',
            'text': (u'Подарите кофе другу. '
                     u'Для этого укажите его имя и телефон. '
                     u'Приложение предложит вам отправить ссылку. '
                     u'Перешлите ссылку своему другу (не меняйте адрес). '
                     u'С вашей карты будет списано 350 рублей, '
                     u'на которые ваш друг сможет получить любой напиток в кофейне Даблби.')
        })


class GetSharedInfo(ApiHandler):  # todo: remove?
    def get(self):
        text_id, text = ('a', (u'Пригласи друга и получи кружку кофе в подарок. '
                               u'Ты делишься ссылкой c друзьями. '
                               u'Друг ставит приложение Даблби и заказывает кофе с 50% скидкой. '
                               u'Ты получаешь бесплатную кружку кофе'))

        url_template = "http://dblb.mobi/get/%%s%s%s"
        ua = self.request.headers["User-Agent"]
        platform_part = "a" if "Android" in ua else "i"
        client_id = self.request.get("client_id")
        client_id_part = "" if not client_id else ("/" + client_id)
        campaign_url_template = url_template % (platform_part, client_id_part)

        self.render_json({
            'image_url': 'http://empatika-doubleb-test.appspot.com/images/shared_image_2.png',
            'fb_android_image_url': 'http://empatika-doubleb-test.appspot.com/images/shared_image_2.png',
            #'text_share_new_order': TEXT,
            'text_share_about_app': "Советую попробовать это интересное приложение для заказа кофе в 3 клика:",
            'app_url': campaign_url_template % text_id,
            'about_url': campaign_url_template % 'd',
            'screen_title': text,
            'screen_text': ' '
        })


class GetInvitationUrlHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        share = Share(share_type=branch_io.INVITATION, sender=client.key)
        share.put()

        values = get_general_shared_dict()

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

        values['urls'] = urls

        self.render_json(values)


class GetGiftUrlHandler(ApiHandler):
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
            'text': (u'%s, разреши угостить тебя чашкой кофе. '
                     u'Чтобы получить ее, пройди по ссылке %s, установи приложение Даблби. '
                     u'Закажи в любой кофейне из списка любой напиток и расплатись подарочной кружкой.') %
                    (name, url)
        })

    def post(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        item_id = self.request.get_range('item_id')
        item = MenuItem.get_by_id(item_id)
        if not item:
            self.abort(400)
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
                success, result = alfa_bank.create_simple(item.float_price, order_id, return_url, alpha_client_id)
                if success:
                    success, error = alfa_bank.hold_and_check(result, binding_id)
                else:
                    error = result
                if not success:
                    self.send_error(error)
                else:
                    gift = SharedGift(client_id=client_id, total_sum=item.float_price, order_id=order_id,
                                      payment_type_id=payment_type_id, payment_id=result)
                    self.success(client, gift=gift, name=recipient_name, phone=recipient_phone)
            else:
                self.send_error(u'Возможна оплата только картой')
        else:
            self.send_error(u'Данный вид оплаты недоступен')