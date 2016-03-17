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

ORDER_TYPE = 1
SIMPLE_TYPE = 2
REVIEW_TYPE = 3
NEWS_TYPE = 4
PUSH_TYPES = (ORDER_TYPE, SIMPLE_TYPE, REVIEW_TYPE, NEWS_TYPE)


class Push(object):
    """Base abstract class for notifications"""

    def __init__(self, text, device_type, push_id=None):
        """
        Initializer for Push class. Keeps two base parameters text and device_type and sets
        other required parameters to None
        :param text: text to display in notification
        :param device_type: int parameter, defined in constants IOS_DEVICE = 0, ANDROID_DEVICE = 1
        """
        self.text = text
        self.device_type = device_type
        self.push_id = push_id

    def _send_push(self):
        from models.config.config import config

        logging.debug("data:{}, dev_type: {}, parsekey: {}, parserest: {}".
                      format(self.data, self.device_type, config.PARSE_APP_API_KEY, config.PARSE_REST_API_KEY))
        if not self.data or self.device_type not in DEVICE_CHOICES or not config.PARSE_APP_API_KEY or not config.PARSE_REST_API_KEY:
            logging.warning(u'Невозможно послать уведомление, data=%s, device_type=%s' % (self.data, self.device_type))
            return
        payload = {
            'channels': self.channels,
            'type': DEVICE_TYPE_MAP[self.device_type],
            'expiry': timestamp(datetime.datetime.utcnow() + datetime.timedelta(days=365)),
            'data': self.data,
        }
        headers = {
            'Content-Type': 'application/json',
            'X-Parse-Application-Id': config.PARSE_APP_API_KEY,
            'X-Parse-REST-API-Key': config.PARSE_REST_API_KEY
        }
        logging.debug(headers)
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

    @property
    def data(self):
        if self.device_type == IOS_DEVICE:
            return {
                'alert': self.text,
                'sound': 'push.caf',
                'should_popup': self.should_popup,
                'type': self.push_type if self.push_type != SIMPLE_TYPE else 999999,  # todo ios v6 fuckup
                'analytics_id': self.push_id,
            }
        elif self.device_type == ANDROID_DEVICE:
            return {
                'text': self.text,
                'head': self.header,
                'action': 'com.empatika.doubleb.push',
                'should_popup': self.should_popup,
                'type': self.push_type,
                'analytics_id': self.push_id,
            }


class OrderPush(Push):
    """Class for notification that are displayed after user have ordered something
    """

    def __init__(self, text, order, namespace, push_id=None):
        """
        Initializes OrderPush
        :param text: text to put in notification
        :param order: order which info have to be pushed
        """
        super(OrderPush, self).__init__(text, order.device_type, push_id)
        self.order = order
        self.should_popup = True
        self.push_type = ORDER_TYPE
        self.header = u'Заказ %s' % self.order.key.id()

        order_channel = get_channels(namespace)[ORDER_CHANNEL] % self.order.key.id()
        order_channel = fuckup_order_channel(order_channel, self.order)
        self.channels = [order_channel]

    @property
    def data(self):
        _data = super(OrderPush, self).data

        if _data:
            _data.update({
                'order_id': str(self.order.key.id()),
                'order_status': int(self.order.status)
            })
        return _data

    def send(self, new_time=None, silent=False):
        """Sends notification to selected namespaces
        :param new_time: optional param to set time to send notification. If not specified sets to None
        :param silent
        """
        if new_time:
            self.data['timestamp'] = timestamp(new_time)
            self.data['time_str'] = self.order.delivery_time_str
        if silent:
            self.data['content-available'] = 1

        return super(OrderPush, self)._send_push()


class BaseSimplePush(Push):
    def __init__(self, text, should_popup, header,
                 client=None, namespace=None, channels=None, device_type=None, push_id=None):

        logging.debug(u"client: {}, namespace: {}, channels: {}, device_type: {}"
                      .format(client, namespace, channels, device_type))

        if client is not None and namespace is not None:
            device_type = client.device_type
            client_channel = get_channels(namespace)[CLIENT_CHANNEL] % client.key.id()
            self.channels = [client_channel]
            self.device_type = client.device_type

            logging.debug('{}'.format(self.channels))

            super(BaseSimplePush, self).__init__(text, device_type, push_id)

        if channels is not None and device_type is not None:
            super(BaseSimplePush, self).__init__(text, device_type, push_id)
            self.channels = channels
            self.device_type = device_type

        self.should_popup = should_popup
        self.header = header
        self.push_type = None

    @property
    def data(self):
        return super(BaseSimplePush, self).data

    def send(self):
        return self._send_push()


class SimplePush(BaseSimplePush):
    """Simple push class for customizable notifications with custom text, title and full text
    Notification can be created either to send some client or to custom channels
    """

    def __init__(self, text, should_popup, full_text, header,
                 client=None, namespace=None, channels=None, device_type=None, push_id=None):
        super(SimplePush, self).__init__(text=text, should_popup=should_popup, header=header,
                                         client=client, namespace=namespace,
                                         channels=channels, device_type=device_type, push_id=push_id)

        self.full_text = full_text
        self.push_type = SIMPLE_TYPE

    @property
    def data(self):
        _data = super(SimplePush, self).data
        if _data:
            _data.update({
                'full_text': self.full_text
            })
        return _data


class ReviewPush(Push):
    def __init__(self, order, push_id):
        client = Client.get(order.client_id)
        device_type = client.device_type
        self.order = order
        self.push_type = REVIEW_TYPE
        text = u'Оставьте отзыв о вашем заказе'
        super(ReviewPush, self).__init__(text, device_type, push_id)
        self.header = u'Оцените заказ'
        self.should_popup = False
        client_channel = get_channels(order.key.namespace())[CLIENT_CHANNEL] % client.key.id()
        self.channels = [client_channel]

    @property
    def data(self):
        _data = super(ReviewPush, self).data
        if _data:
            _data.update({
                'review': {
                    'order_id': str(self.order.key.id())
                }
            })
        return _data

    def send(self):
        return super(ReviewPush, self)._send_push()


class NewsPush(BaseSimplePush):
    def __init__(self, news, client=None, namespace=None, channels=None, device_type=None, push_id=None):
        text = news.text
        head = news.title

        super(NewsPush, self).__init__(text, False, head, client, namespace, channels, device_type, push_id=push_id)

        self.news = news
        self.push_type = NEWS_TYPE

    @property
    def data(self):
        _data = super(NewsPush, self).data
        if _data:
            news_dict = self.news.dict_with_title()
            _data.update({
                'news_data': news_dict
            })
        return _data
