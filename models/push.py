# coding=utf-8
import datetime
import json
import logging
from abc import ABCMeta

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


class Push(object):
    """Base abstract class for notifications"""

    __metaclass__ = ABCMeta

    def __init__(self, text, device_type):
        """
        Initializer for Push class. Keeps two base parameters text and device_type and sets
        other required parameters to None
        :param text: text to display in notification
        :param device_type: int parameter, defined in constants IOS_DEVICE = 0, ANDROID_DEVICE = 1
        """
        self.text = text
        self.device_type = device_type
        self.channels = None
        self.should_popup = None
        self.push_type = None
        self.header = None

    def _make_push_data(self):
        if self.device_type == IOS_DEVICE:
            self.data = {
                'alert': self.text,
                'sound': 'push.caf',
                'should_popup': self.should_popup,
                'type': self.push_type
            }
        elif self.device_type == ANDROID_DEVICE:
            self.data = {
                'text': self.text,
                'head': self.header,
                'action': 'com.empatika.doubleb.push',
                'should_popup': self.should_popup,
                'type': self.push_type
            }

    def _send_push(self):
        if not self.data or self.device_type not in DEVICE_CHOICES:
            logging.warning(u'Невозможно послать уведомление, data=%s, device_type=%s' % (self.data, self.device_type))
            return
        payload = {
            'channels': self.channels,
            'type': DEVICE_TYPE_MAP[self.device_type],
            'expiry': timestamp(datetime.datetime.utcnow() + datetime.timedelta(days=365)),
            'data': self.data
        }
        headers = {
            'Content-Type': 'application/json',
            'X-Parse-Application-Id': config.PARSE_APP_API_KEY,
            'X-Parse-REST-API-Key': config.PARSE_REST_API_KEY
        }
        try:
            result = json.loads(urlfetch.fetch('https://api.parse.com/1/push',
                                               payload=json.dumps(payload),
                                               method='POST',
                                               headers=headers,
                                               validate_certificate=False,
                                               deadline=10)
                                .content)
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


class OrderPush(object, Push):
    """Class for notification that are displayed after user have ordered something
    """

    def __init__(self, text, device_type, order):
        """
        Initializes OrderPush
        :param text: text to put in notification
        :param device_type: int parameter, defined in constants IOS_DEVICE = 0, ANDROID_DEVICE = 1
        :param order: order which info have to be pushed
        """
        super(OrderPush, self).__init__(text, device_type)
        self.order = order
        self.should_popup = True
        self.push_type = ORDER_TYPE
        self.header = u'Заказ %s' % self.order.key.id()

    def _make_push_data(self):
        """Creates dictionary data of notification"""
        self.data = super(OrderPush, self)._make_push_data()
        if self.data:
            self.data.update({
                'order_id': str(self.order.key.id()),
                'order_status': int(self.order.status)
            })

    def send(self, namespace, new_time=None, silent=False):
        """Sends notification to selected namespaces
        :param new_time: optional param to set time to send notification. If not specified sets to None
        :param silent
        """
        self._make_push_data()
        if new_time:
            self.data['timestamp'] = timestamp(new_time)
            self.data['time_str'] = self.order.delivery_time_str
        if silent:
            self.data['content-available'] = 1
        order_channel = get_channels(namespace)[ORDER_CHANNEL] % self.order.key.id()
        order_channel = fuckup_order_channel(order_channel, self.order)
        self.channels = [order_channel]

        return super(OrderPush, self)._send_push()


class BaseSimplePush(object, Push):
    __metaclass__ = ABCMeta

    def __init__(self, text, should_popup, header,
                 client=None, namespace=None, channels=None, device_type=None):

        if client and namespace:
            device_type = client.device_type
            client_channel = get_channels(namespace)[CLIENT_CHANNEL] % client.key.id()
            self.channels = [client_channel]
            super(BaseSimplePush, self).__init__(text, device_type)
        elif channels and device_type:
            self.channels = channels
            self.device_type = device_type
        else:
            raise Exception('You must specify either client and namespace or channels and device_type')
        self.should_popup = should_popup
        self.header = header
        self.push_type = None

    def _make_push_data(self):
        super(BaseSimplePush, self)._make_push_data()

    def send(self):
        return super(BaseSimplePush, self)._send_push()


class SimplePush(object, BaseSimplePush):
    """Simple push class for customizable notifications with custom text, title and full text
    Notification can be created either to send some client or to custom channels
    """

    def __init__(self, text, should_popup, full_text, header,
                 client=None, namespace=None, channels=None, device_type=None):
        super(SimplePush, self).__init__(text, should_popup, header, client, namespace, channels, device_type)

        self.full_text = full_text

    def _make_push_data(self):
        super(SimplePush, self)._make_push_data()
        if self.data:
            self.data.update({
                'full_text': self.full_text
            })

    def send(self):
        return super(SimplePush, self).send()


class ReviewPush(object, Push):
    def __init__(self, order):
        client = Client.get(order.client_id)
        device_type = client.device_type
        text = u'Оставьте отзыв о вашем заказе'
        super(ReviewPush, self).__init__(text, device_type)
        self.header = u'Оцените заказ'
        self.should_popup = False
        client_channel = get_channels(order.key.namespace())[CLIENT_CHANNEL] % client.key.id()
        self.channels = [client_channel]

    def _make_push_data(self):
        super(ReviewPush, self)._make_push_data()
        if self.data:
            self.data.update({
                'review': {
                    'order_id': str(self.order.key.id())
                }
            })

    def send(self):
        return super(ReviewPush, self)._send_push()


class NewsPush(object, BaseSimplePush):
    def __init__(self, news, client, namespace, channels, device_type):
        news_dict = news.dict()
        text = news_dict['text']
        head = news_dict['title']
        self.news = news

        super(NewsPush, self).__init__(text, False, head, client, namespace, channels, device_type)

    def _make_push_data(self):
        news_dict = self.news.dict()
        if self.data:
            self.data.update({
                'news_data': news_dict
            })

    def send(self):
        return super(NewsPush, self).send()
