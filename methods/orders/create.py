# coding=utf-8
import json
from google.appengine.api import taskqueue
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from webapp2_extras import security
from models import Order

from models.config.config import config, EMAIL_FROM
from handlers.api.paypal import paypal
from handlers.email_api.order import POSTPONE_MINUTES
from handlers.web_admin.web.company.delivery.orders import order_items_values
from methods import alfa_bank
from methods.emails.admins import send_error
from methods.emails.postmark import send_email
from methods.sms.sms_pilot import send_sms
from models.payment_types import PAYMENT_TYPE_MAP
from models.share import SharedPromo
from models.venue import DELIVERY_MAP, DELIVERY, Address, Venue

__author__ = 'dvpermyakov'


def card_payment_performing(payment_json, amount, order, put_order=True):
    binding_id = payment_json.get('binding_id')
    client_id = payment_json.get('client_id')
    return_url = payment_json.get('return_url')
    if not binding_id or not client_id or not return_url:
        return False, u'Карта не найдена'

    legal = Venue.get(order.venue_id).legal.get()

    try:
        success, result = alfa_bank.create_simple(legal.alfa_login, legal.alfa_password, amount, order.key.id(), return_url,
                                                  client_id)
    except Exception as e:
        send_error("Alfa error", "Alfa failure", str(e))
        success, result = False, u'Не удалось произвести оплату'

    if not success:
        return success, result

    order.payment_id = result
    if put_order:
        order.put()
    success, error = alfa_bank.hold_and_check(legal.alfa_login, legal.alfa_password, order.payment_id, binding_id)
    if not success:
        error = u"Не удалось произвести оплату. %s" % error
    return success, error


def paypal_payment_performing(payment_json, amount, order, client, put_order=True):
    correlation_id = payment_json['correlation_id']
    try:
        success, info = paypal.authorize(order.key.id(), amount / 100.0, client.paypal_refresh_token, correlation_id)
    except Exception as e:
        success, info = False, str(e)
    if success:
        order.payment_id = info
        if put_order:
            order.put()
    error = None
    if not success:
        error = u'Не удалось произвести оплату'
        if not isinstance(info, (str, unicode)):
            info = json.dumps(info)
        send_error("Paypal error", "Paypal failure", info)
    return success, error


def send_client_sms_task(order, namespace):
    SECONDS_WAITING_BEFORE_SMS = 15
    taskqueue.add(url='/task/check_order_success', params={
        'order_id': order.key.id(),
        'namespace': namespace
    }, countdown=SECONDS_WAITING_BEFORE_SMS)


def send_venue_sms(venue, order, move=False):
    if venue.phones:
        if move:
            text = u'Заказ №%s перенесен на эту точку приготовления' % order.key.id()
        else:
            text = u'Новый заказ №%s поступил в систему из мобильного приложения' % order.key.id()
        send_sms(venue.phones, text)


def send_demo_sms(client):
    text = u'Поздравляем! На Вашу почту поступил тестовый заказ. Хотите боевой?\nhttp://rbcn.mobi/'
    try:
        send_sms([client.tel], text, company_footer=False)
    except Exception as e:
        error_text = str(e)
        error_text += u' В демо компании "%s" (%s).' % (config.APP_NAME, namespace_manager.get_namespace())
        send_error('sms_error', 'Send sms', error_text)


def send_venue_email(venue, order, host_url, jinja2, move=False):
    if venue.emails:
        if move:
            text = u'Заказ №%s перенесен на эту точку приготовления' % order.key.id()
        else:
            text = u'Новый заказ №%s поступил в систему из мобильного приложения' % order.key.id()
        item_values = order_items_values(order)
        item_values['venue'] = venue
        item_values['delivery_type_str'] = DELIVERY_MAP[order.delivery_type]
        order.payment_type_str = PAYMENT_TYPE_MAP[order.payment_type_id]
        if config.EMAIL_REQUESTS:
            order.email_key_done = security.generate_random_string(entropy=256)
            order.email_key_cancel = security.generate_random_string(entropy=256)
            order.email_key_postpone = security.generate_random_string(entropy=256)
            if order.delivery_type == DELIVERY:
                order.email_key_confirm = security.generate_random_string(entropy=256)
            order.put()

            item_values['done_url'] = '%s/email/order/close?key=%s' % (host_url, order.email_key_done)
            item_values['cancel_url'] = '%s/email/order/cancel?key=%s' % (host_url, order.email_key_cancel)
            item_values['postpone_url'] = '%s/email/order/postpone?key=%s' % (host_url, order.email_key_postpone)
            item_values['minutes'] = POSTPONE_MINUTES
            if order.delivery_type == DELIVERY:
                item_values['confirm_url'] = '%s/email/order/confirm?key=%s' % (host_url, order.email_key_confirm)
        for email in venue.emails:
            if email:
                deferred.defer(send_email, EMAIL_FROM, email, text,
                               jinja2.render_template('/company/delivery/items.html', **item_values))


def need_to_show_share_invitation(client):
    module = config.SHARE_INVITATION_MODULE
    if not module or not module.status:
        return False
    if not module.after_order:
        return False
    if SharedPromo.query(SharedPromo.sender == client.key, SharedPromo.status == SharedPromo.DONE).get():
        return False
    count = Order.query(Order.client_id == client.key.id()).count()
    if count % module.after_number_order != 0:
        return False
    return True


def set_address_obj(address_json, order):
    address_args = {
        'lat': float(address_json['coordinates']['lat']) if address_json['coordinates']['lat'] else None,
        'lon': float(address_json['coordinates']['lon']) if address_json['coordinates']['lon'] else None,
        'country': address_json['address'].get('country'),
        'city': address_json['address'].get('city'),
        'street': address_json['address'].get('street'),
        'area': address_json['address'].get('area'),
        'home': address_json['address'].get('home'),
        'flat': address_json['address'].get('flat'),
        'comment': address_json['address'].get('comment'),
    }
    address_obj = Address(**address_args)
    address_obj.comment = address_json['comment'] if address_json.get('comment') else None
    order.address = address_obj
