# coding=utf-8
import logging

from google.appengine.ext import ndb

from methods.rendering import timestamp
from models.client import Client

# from models.config.inactive_clients import CONDITIONS, NOT_TYPES
from methods.unique import VERSION, get_temporary_user
from models.config.inactive_clients import NOTIFICATION_TYPES

COMPANY_CHANNEL = 'company'
ORDER_CHANNEL = 'order'
CLIENT_CHANNEL = 'client'
VENUE_CHANNEL = 'venue'


def get_channels(namespace):
    return {
        COMPANY_CHANNEL: '%s_company' % namespace,
        ORDER_CHANNEL: '%s_order_%s' % (namespace, '%s'),
        CLIENT_CHANNEL: '%s_client_%s' % (namespace, '%s'),
        VENUE_CHANNEL: '%s_venue_%s' % (namespace, '%s')
    }


STATUS_CREATED = 0
STATUS_ACTIVE = 1
STATUS_DONE = 2
STATUS_CANCELLED = 3
NOTIFICATION_STATUS_CHOICES = (STATUS_CREATED, STATUS_ACTIVE, STATUS_DONE, STATUS_CANCELLED)
NOTIFICATION_STATUS_MAP = {
    STATUS_CREATED: u'Создано',
    STATUS_ACTIVE: u'Активно',
    STATUS_DONE: u'Завершено',
    STATUS_CANCELLED: u'Отменено'
}


class Channel(ndb.Model):
    name = ndb.StringProperty(required=True)
    channel = ndb.StringProperty(required=True)


class Notification(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.IntegerProperty(choices=NOTIFICATION_STATUS_CHOICES, default=STATUS_CREATED)
    start = ndb.DateTimeProperty(required=True)
    text = ndb.StringProperty(required=True)
    popup_text = ndb.StringProperty()
    header = ndb.StringProperty()  # it is used for Android
    channels = ndb.LocalStructuredProperty(Channel, repeated=True)
    should_popup = ndb.BooleanProperty(default=False)

    def closed(self):
        self.status = STATUS_DONE
        self.put()

    def cancel(self):
        self.status = STATUS_CANCELLED
        self.put()


class ClientSmsSending(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    client = ndb.KeyProperty(kind=Client, required=True)
    sms_type = ndb.IntegerProperty(choices=NOTIFICATION_TYPES, required=True)


class ClientPushSending(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    client = ndb.KeyProperty(kind=Client, required=True)
    type = ndb.IntegerProperty(choices=NOTIFICATION_TYPES, required=True)


class News(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    start = ndb.DateTimeProperty(required=True)
    title = ndb.StringProperty()
    text = ndb.StringProperty(required=True, indexed=False)
    status = ndb.IntegerProperty(choices=NOTIFICATION_STATUS_CHOICES, default=STATUS_CREATED)
    image_url = ndb.StringProperty(indexed=False)
    notification = ndb.StructuredProperty(Notification)

    def activate(self):
        self.status = STATUS_ACTIVE
        self.put()

    def cancel(self):
        self.status = STATUS_CANCELLED
        self.put()

    def dict_with_title(self):
        return {
            "id": str(self.key.id()),
            "title": self.title or "",
            "text": self.text,
            "start": timestamp(self.start),
            "image_url": self.image_url if self.image_url else None
        }

    def dict_old(self):
        text = self.text
        if self.title:
            text = u"{0}\n{1}".format(self.title, self.text)
        return {
            "id": str(self.key.id()),
            "text": text,
            "start": timestamp(self.start),
            "image_url": self.image_url if self.image_url else None
        }

    def dict(self):
        tu = get_temporary_user()
        if tu[VERSION] <= 5:
            return self.dict_old()
        else:
            return self.dict_with_title()


class Deposit(ndb.Model):
    source = ndb.StringProperty(required=True)
    amount = ndb.IntegerProperty(required=True)  # в рублях


class ReviewPush(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    sent = ndb.DateTimeProperty()
    order = ndb.KeyProperty()  # kind=Order
