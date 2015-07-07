# coding=utf-8
import datetime
import json
import logging
from google.appengine.api import urlfetch
from google.appengine.api.namespace_manager import namespace_manager
from methods.email_mandrill import send_email
from methods.rendering import timestamp
from models.client import DEVICE_TYPE_MAP, IOS_DEVICE, ANDROID_DEVICE, DEVICE_CHOICES
from models.specials import get_channels, ORDER_CHANNEL, CLIENT_CHANNEL
from config import config

IOS_FUCKUP = ['Pastadeli/1.0', 'Pastadeli/1.1', 'ElephantBoutique/1.0', 'MeatMe/1.0']
ANDROID_FUCKUP = ['pastadeli/4', 'pastadeli/5', 'meatme/4', 'meatme/5']


def _send_push(channels, data, device_type):
    if not data or device_type not in DEVICE_CHOICES:
        logging.warning(u'Невозможно послать уведомление, data=%s, device_type=%s' % (data, device_type))
        return
    payload = {
        'channels': channels,
        'type': DEVICE_TYPE_MAP[device_type],
        'expiry': timestamp(datetime.datetime.utcnow() + datetime.timedelta(days=365)),
        'data': data
    }
    headers = {
        'Content-Type': 'application/json',
        'X-Parse-Application-Id': config.PARSE_APP_API_KEY,
        'X-Parse-REST-API-Key': config.PARSE_REST_API_KEY
    }
    try:
        result = json.loads(urlfetch.fetch('https://api.parse.com/1/push', payload=json.dumps(payload), method='POST',
                            headers=headers, validate_certificate=False, deadline=10).content)
        logging.info(result)
        if result and (result.get('code') or result.get('error')):
            text = u'Namespace = %s\nCode = %s, Error = %s' % (namespace_manager.get_namespace(), result.get('code'), result.get('error'))
            send_email('dvpermyakov1@gmail.com', 'dvpermyakov1@gmail.com', u'Ошибка Parse', text)
    except Exception as e:
        text = str(e)
        send_email('dvpermyakov1@gmail.com', 'dvpermyakov1@gmail.com', u'Parse упал', text)
        result = None
    return result


def _make_push_data(text, header, device_type):
    if device_type == IOS_DEVICE:
        return {
            'alert': text,
        }
    elif device_type == ANDROID_DEVICE:
        return {
            'text': text,
            'head': header,
            'action': 'com.empatika.doubleb.push'
        }
    return None


def _make_order_push_data(order, text):
    data = _make_push_data(text, u"Заказ %s" % order.key.id(), order.device_type)
    if data:
        if order.device_type == IOS_DEVICE:
            data.update({
                'sound': 'push.caf',
                'order_id': str(order.key.id()),
                'order_status': int(order.status)
            })
        return data
    else:
        return None


def _make_share_gift_push_data(client, text):
    data = _make_push_data(text, u'Вам прислали подарок!', client.device_type)
    if data:
        data.update({
            'share_gift': True
        })
        return data
    else:
        return None


def send_order_push(order, text, namespace, new_time=None, silent=False):
    data = _make_order_push_data(order, text)
    if new_time:
        data['timestamp'] = timestamp(new_time)
    if silent:
        data['content-available'] = 1
    order_channel = get_channels(namespace)[ORDER_CHANNEL] % order.key.id()
    ####### IOS, ANDROID FUCKUP
    if 'Android' in order.user_agent:
        for fuckup in ANDROID_FUCKUP:
            if fuckup in order.user_agent:
                order_channel = 'order_%s' % order.key.id()
    if 'iOS' in order.user_agent:
        for fuckup in IOS_FUCKUP:
            if fuckup in order.user_agent:
                order_channel = 'order_%s' % order.key.id()
    #######
    return _send_push([order_channel], data, order.device_type)


def send_client_push(client, text, header, namespace):
    data = _make_push_data(text, header, client.device_type)
    client_channel = get_channels(namespace)[CLIENT_CHANNEL] % client.key.id()
    return _send_push([client_channel], data, client.device_type)


def send_multichannel_push(text, header, channels, device_type):
    data = _make_push_data(text, header, device_type)
    return _send_push(channels, data, device_type)


def send_share_gift_push(client, text, namespace):
    data = _make_share_gift_push_data(client, text)
    client_channel = get_channels(namespace)[CLIENT_CHANNEL] % client.key.id()
    return _send_push([client_channel], data, client.device_type)