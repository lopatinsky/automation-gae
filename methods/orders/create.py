# coding=utf-8
from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from webapp2_extras import security
from config import config
from handlers.email_api.order import POSTPONE_MINUTES
from handlers.web_admin.web.company.delivery.orders import order_items_values
from methods.email import send_error
from methods.email_mandrill import send_email
from methods.twilio import send_sms
from models.payment_types import PAYMENT_TYPE_MAP
from models.venue import DELIVERY_MAP, DELIVERY

__author__ = 'dvpermyakov'

EMAIL_FROM = 'noreply-order@ru-beacon.ru'


def send_venue_sms(venue, order):
    if venue.phones:
        text = u'Новый заказ №%s поступил в систему из мобильного приложения' % order.key.id()
        for phone in venue.phones:
            try:
                send_sms([phone], text)
            except Exception as e:
                error_text = str(e)
                error_text += u' В компании "%s" (%s).' % (config.APP_NAME, namespace_manager.get_namespace())
                send_error('sms_error', 'Send sms', error_text)


def send_venue_email(venue, order, url, jinja2):
    if venue.emails:
        text = u'Новый заказ №%s поступил в систему из мобильного приложения' % order.key.id()
        item_values = order_items_values(order)
        item_values['venue'] = venue
        item_values['delivery_type_str'] = DELIVERY_MAP[order.device_type]
        order.payment_type_str = PAYMENT_TYPE_MAP[order.payment_type_id]
        if config.EMAIL_REQUESTS:
            order.email_key_done = security.generate_random_string(entropy=256)
            order.email_key_cancel = security.generate_random_string(entropy=256)
            order.email_key_postpone = security.generate_random_string(entropy=256)
            if order.delivery_type == DELIVERY:
                order.email_key_confirm = security.generate_random_string(entropy=256)
            order.put()

            base_url = urlparse(url).hostname
            item_values['done_url'] = 'http://%s/email/order/close?key=%s' % (base_url, order.email_key_done)
            item_values['cancel_url'] = 'http://%s/email/order/cancel?key=%s' % (base_url, order.email_key_cancel)
            item_values['postpone_url'] = 'http://%s/email/order/postpone?key=%s' % (base_url, order.email_key_postpone)
            item_values['minutes'] = POSTPONE_MINUTES
            if order.delivery_type == DELIVERY:
                item_values['confirm_url'] = 'http://%s/email/order/confirm?key=%s' % (base_url, order.email_key_confirm)
        for email in venue.emails:
            deferred.defer(send_email, EMAIL_FROM, email, text,
                           jinja2.render_template('/company/delivery/items.html', **item_values))
