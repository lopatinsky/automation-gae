# coding: utf-8
from config import Config

__author__ = 'dvpermyakov'

import time
from models.payment_types import CARD_PAYMENT_TYPE
from base import ApiHandler
from methods import branch_io, alfa_bank
from models import Share, Client, PaymentType, STATUS_AVAILABLE, SharedGift
from models.share import SharedGiftMenuItem
import logging


def _get_gift_dict():
    config = Config.get()
    return {
        'head': config.SHARED_GIFT_HEAD,
        'text': config.SHARED_GIFT_TEXT,
        'image': config.SHARED_GIFT_IMAGE_URL
    }


def _get_about_gift_dict():
    config = Config.get()
    return {
        'head': config.SHARED_ABOUT_GIFT_HEAD,
        'text': config.SHARED_ABOUT_GIFT_TEXT,
        'image': config.SHARED_ABOUT_GIFT_IMAGE_URL
    }


def _get_invitation_dict():
    config = Config.get()
    return {
        'head': config.SHARED_INVITATION_HEAD,
        'text': config.SHARED_INVITATION_TEXT,
        'image': config.SHARED_INVITATION_IMAGE_URL
    }


def _get_about_invitation_dict():
    config = Config.get()
    return {
        'head': config.SHARED_ABOUT_INVITATION_HEAD,
        'text': config.SHARED_ABOUT_INVITATION_TEXT,
        'image': config.SHARED_ABOUT_INVITATION_IMAGE_URL
    }


def _get_share_dict():
    config = Config.get()
    return {
        'head': config.SHARED_SHARE_HEAD,
        'text': config.SHARED_SHARE_TEXT,
        'image': config.SHARED_SHARE_IMAGE_URL
    }


class GiftInfoHandler(ApiHandler):
    def get(self):
        self.render_json(_get_about_gift_dict())


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

        self.render_json(_get_share_dict())


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

        self.render_json({
            'info': _get_invitation_dict(),
            'about': _get_about_invitation_dict(),
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
        values = _get_gift_dict()
        values['text'] = values['text'] % url
        self.render_json(values)

    def post(self):
        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        item_id = self.request.get_range('item_id')
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
                success, result = alfa_bank.create_simple(item.float_price, order_id, return_url, alpha_client_id)
                if success:
                    success, error = alfa_bank.hold_and_check(result, binding_id)
                else:
                    error = result
                if not success:
                    self.send_error(error)
                else:
                    gift = SharedGift(client_id=client_id, total_sum=item.float_price, order_id=order_id,
                                      payment_type_id=payment_type_id, payment_id=result, share_item=share_item.key,
                                      recipient_name=recipient_name, recipient_phone=recipient_phone)
                    self.success(client, gift=gift, name=recipient_name, phone=recipient_phone)
            else:
                self.send_error(u'Возможна оплата только картой')
        else:
            self.send_error(u'Данный вид оплаты недоступен')