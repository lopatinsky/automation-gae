# coding=utf-8
import datetime
import json
import logging
from google.appengine.api import urlfetch
from methods.rendering import timestamp
from models.client import DEVICE_TYPE_MAP, IOS_DEVICE, ANDROID_DEVICE
from models.specials import get_channels, ORDER_CHANNEL, CLIENT_CHANNEL
from config import config


def send_push(channels, data, device_type):
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
    result = urlfetch.fetch('https://api.parse.com/1/push', payload=json.dumps(payload), method='POST',
                            headers=headers, validate_certificate=False, deadline=10).content
    logging.info(result)
    return json.loads(result)


def make_push_data(text, header, device_type):
    if device_type == IOS_DEVICE:
        return {
            'alert': text,
        }
    elif device_type == ANDROID_DEVICE:
        return {
            'text': text,
            'head': header,
            'action': 'com.empatika.doubleb.push'  # todo: set it
        }
    return None


def make_order_push_data(order_id, order_status, text, device_type):
    data = make_push_data(text, u"Заказ %s" % order_id, device_type)
    if data:
        if device_type == IOS_DEVICE:
            data.update({
                'sound': 'push.caf',
                'order_id': str(order_id),
                'order_status': int(order_status)
            })
        return data
    else:
        return None


def send_order_push(order_id, order_status, text, device_type, namespace, new_time=None, silent=False):
    data = make_order_push_data(order_id, order_status, text, device_type)
    if new_time:
        data['timestamp'] = timestamp(new_time)
    if silent:
        data['content-available'] = 1
    order_channel = get_channels(namespace)[ORDER_CHANNEL] % order_id
    return send_push([order_channel], data, device_type)


def send_reminder_push(client_id, client_name, client_score, namespace):  # todo: update this
    if client_name:
        text = u'%s, Вас давно не было в Даблби. Заходите, как будете рядом.' % client_name
    else:
        text = u'Вас давно не было в Даблби. Заходите, как будете рядом.'
    if client_score:
        if client_score == 1:
            text += u' Вы уже накопили %s балл. За 5 вам полагается подарок.' % client_score
        elif client_score == 2 or client_score == 3 or client_score == 4:
            text += u' Вы уже накопили %s балла. За 5 вам полагается подарок.' % client_score
    data = {
        'text': text,
        'head': 'DoubleB',
        'action': 'com.empatika.doubleb.push',
        'marker': 'send_reminder'
    }
    client_channel = get_channels(namespace)[CLIENT_CHANNEL] % client_id
    return send_push([client_channel], data, ANDROID_DEVICE)


def send_order_ready_push(order, namespace):
    send_order_push(order.key.id(), order.status,
                    u"Заказ №%s выдан." % str(order.key.id()),
                    order.device_type, namespace, silent=True)
