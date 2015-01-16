# coding=utf-8
import datetime
import json
import logging
from google.appengine.api import urlfetch
from methods.rendering import timestamp
from models import IOS_DEVICE, ANDROID_DEVICE

PARSE_APPLICATION_ID = 'sSS9VgN9K2sU3ycxzwQlwrBZPFlEe7OvSNZQDjQe'
PARSE_API_KEY = 'kD69rsD7G0ZpxUgkutIF4eFwJF0tnWDQSghVMLt3'

DEVICE_TYPE_MAP = {
    IOS_DEVICE: 'ios',
    ANDROID_DEVICE: 'android'
}


def send_push(channel, data, device_type):
    payload = {
        'channel': channel,
        'type': DEVICE_TYPE_MAP[device_type],
        'expiry': timestamp(datetime.datetime.utcnow() + datetime.timedelta(days=365)),
        'data': data
    }
    headers = {
        'Content-Type': 'application/json',
        'X-Parse-Application-Id': PARSE_APPLICATION_ID,
        'X-Parse-REST-API-Key': PARSE_API_KEY
    }
    result = urlfetch.fetch('https://api.parse.com/1/push', payload=json.dumps(payload), method='POST',
                            headers=headers, validate_certificate=False).content
    logging.info(result)
    return json.loads(result)


def make_order_push_data(order_id, order_status, text, device_type):
    if device_type == IOS_DEVICE:
        return {
            'alert': text,
            'sound': 'push.caf',
            'order_id': str(order_id),
            'order_status': int(order_status)
        }
    elif device_type == ANDROID_DEVICE:
        return {
            'text': text,
            'head': u"Заказ %s" % order_id,
            'action': 'com.empatika.doubleb.push'
        }
    return None


def send_order_push(order_id, order_status, text, device_type, new_time=None, silent=False):
    data = make_order_push_data(order_id, order_status, text, device_type)
    if new_time:
        data['timestamp'] = timestamp(new_time)
    if silent:
        data['content-available'] = 1
    return send_push("order_%s" % order_id, data, device_type)


def send_reminder_push(client_id, client_name, client_score):
    text = u'%s, Вас давно не было в Даблби. Заходите, как будете рядом.' % client_name
    if client_score:
        text += u' У Вас на балансе накоплено %s балла. а за 5 - будет подарок.' % client_score
    data = {
        'text': text,
        'head': 'DoubleB',
        'action': 'com.empatika.doubleb.push',
        'marker': 'send_reminder'
    }
    return send_push('client_%s' % client_id, data, ANDROID_DEVICE)
