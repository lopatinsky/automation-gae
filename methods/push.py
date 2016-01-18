# coding=utf-8
import datetime
import json
import logging

from google.appengine.api import urlfetch

from google.appengine.api.namespace_manager import namespace_manager

from methods.emails.admins import send_error
from methods.fuckups import fuckup_order_channel
from methods.rendering import timestamp
from models.client import DEVICE_TYPE_MAP, IOS_DEVICE, ANDROID_DEVICE, DEVICE_CHOICES, Client
from models.specials import get_channels, ORDER_CHANNEL, CLIENT_CHANNEL
from models.config.config import config

ORDER_TYPE = 1
SIMPLE_TYPE = 2
REVIEW_TYPE = 3
NEWS_TYPE = 4
PUSH_TYPES = (ORDER_TYPE, SIMPLE_TYPE, REVIEW_TYPE, NEWS_TYPE)


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
            text = u'Namespace = %s\nCode = %s, Error = %s' % (
                namespace_manager.get_namespace(), result.get('code'), result.get('error'))
            send_error('push', u'Ошибка Parse', text)
    except Exception as e:
        text = str(e)
        send_error('push', u'Parse упал', text)
        result = None
    return result


def _make_push_data(text, header, device_type, should_popup, push_type):
    if device_type == IOS_DEVICE:
        return {
            'alert': text,
            'sound': 'push.caf',
            'should_popup': should_popup,
            'type': push_type
        }
    elif device_type == ANDROID_DEVICE:
        return {
            'text': text,
            'head': header,
            'action': 'com.empatika.doubleb.push',
            'should_popup': should_popup,
            'type': push_type
        }
    return None


def _make_order_push_data(order, text):
    data = _make_push_data(text, u"Заказ %s" % order.number, order.device_type, True, ORDER_TYPE)
    if data:
        data.update({
            'order_id': str(order.key.id()),
            'order_status': int(order.status),
        })
    return data


def _make_order_review_push_data(client, order):
    head = u'Оцените заказ'
    text = u'Оставьте отзыв о Вашем заказе!'
    data = _make_push_data(text, head, client.device_type, False, REVIEW_TYPE)
    if data:
        data.update({
            'review': {
                'order_id': str(order.key.id())
            }
        })
    return data


def _make_news_push_data(client, news):
    news_dict = news.dict()
    text = news_dict['text']
    # head = 'somenews'
    head = news_dict['title']
    data = _make_push_data(text, head, client.device_type, True, NEWS_TYPE)
    if data:
        data.update({
            'news_data': news_dict
        })


def _make_simple_push_data(client, head, text, full_text):
    data = _make_push_data(text, head, client.device_type, True, SIMPLE_TYPE)
    if data:
        data.update({
            'full_text': full_text
        })
    return data


def send_order_push(order, text, namespace, new_time=None, silent=False):
    data = _make_order_push_data(order, text)
    if new_time:
        data['timestamp'] = timestamp(new_time)
        data['time_str'] = order.delivery_time_str
    if silent:
        data['content-available'] = 1
    order_channel = get_channels(namespace)[ORDER_CHANNEL] % order.key.id()
    order_channel = fuckup_order_channel(order_channel, order)
    return _send_push([order_channel], data, order.device_type)


def send_client_push(client, text, header, namespace):
    logging.debug(client)
    data = _make_push_data(text, header, client.device_type, should_popup=True, push_type='')
    client_channel = get_channels(namespace)[CLIENT_CHANNEL] % client.key.id()
    return _send_push([client_channel], data, client.device_type)


def send_multichannel_push(text, header, channels, device_type):
    data = _make_push_data(text, header, device_type)
    return _send_push(channels, data, device_type)


def send_review_push(order):
    client = Client.get(order.client_id)
    data = _make_order_review_push_data(client, order)
    client_channel = get_channels(order.key.namespace())[CLIENT_CHANNEL] % client.key.id()
    return _send_push([client_channel], data, client.device_type)
