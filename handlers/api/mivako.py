# coding=utf-8
import json
import logging
from handlers.api.base import ApiHandler
from methods.emails.postmark import send_email
from methods.orders.validation.validation import set_modifiers, set_price_with_modifiers
from methods.rendering import get_phone
from models import Client, STATUS_UNAVAILABLE
from models.config.config import Config
from models.mivako_gift import Recipient, MivakoGift
from models.share import SharedGiftMenuItem

__author__ = 'dvpermyakov'


class MivakoGetUrlHandler(ApiHandler):
    def send_error(self, error):
        logging.info(error)
        self.response.set_status(400)
        self.render_json({
            'success': False,
            'description': error
        })

    def post(self):
        config = Config.get()
        module = config.MIVAKO_GIFT_MODULE
        if not module or not module.status:
            return self.send_error(u'Даннаая услуга отключена')
        client_id = int(self.request.headers.get('Client-Id') or 0)
        client = Client.get(client_id)
        if not client:
            self.abort(400)
        recipient_name = self.request.get('recipient_name')
        if not recipient_name:
            return self.send_error(u'Введите имя получателя')
        recipient_email = self.request.get('recipient_email')
        recipient_phone = self.request.get('recipient_phone')
        if not recipient_phone:
            return self.send_error(u'Введите номер телефона получателя')
        recipient_phone = get_phone(recipient_phone)
        items_json = json.loads(self.request.get('items'))
        items = set_modifiers(items_json)
        items = set_price_with_modifiers(items)
        if not items:
            return self.send_error(u'Выберите подарок')
        for item in items:
            share_item = SharedGiftMenuItem.get_by_id(item.key.id())
            if not share_item or share_item.status == STATUS_UNAVAILABLE:
                return self.send_error(u'Продукт %s недоступен' % item.title)
        text = u'Имя получателя: %s\n' \
               u'Телефон получателя: %s\n' \
               u'Email получателя: %s\n' \
               u'Подарок: %s' % (recipient_name, recipient_phone, recipient_email,
                                 u', '.join([item.title for item in items]))
        for email in module.emails:
            send_email(None, email, u'Подари другу', text)
        recipient = Recipient(name=recipient_name, phone=recipient_phone, email=recipient_email)
        MivakoGift(items=[item.key for item in items], sender=client.key, recipient=recipient)
        self.render_json({})
