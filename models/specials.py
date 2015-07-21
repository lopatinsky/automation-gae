# coding=utf-8
from google.appengine.ext import ndb
from methods.rendering import timestamp
from models.client import Client

SMS_SUCCESS = 1
SMS_PASSIVE = 2
SMS_CHOICES = (SMS_SUCCESS, SMS_PASSIVE)

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

    def closed(self):
        self.status = STATUS_DONE
        self.put()

    def cancel(self):
        self.status = STATUS_CANCELLED
        self.put()


class ClientNotification(Notification):
    client = ndb.KeyProperty(required=True)


class ClientSmsSending(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    client = ndb.KeyProperty(kind=Client, required=True)
    sms_type = ndb.IntegerProperty(choices=SMS_CHOICES, required=True)


class News(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    start = ndb.DateTimeProperty(required=True)
    end = ndb.DateTimeProperty(required=True)
    text = ndb.StringProperty(required=True, indexed=False)
    status = ndb.IntegerProperty(choices=NOTIFICATION_STATUS_CHOICES, default=STATUS_CREATED)
    image_url = ndb.StringProperty(required=True, indexed=False)

    def activate(self):
        self.status = STATUS_ACTIVE
        self.put()

    def deactivate(self):
        self.status = STATUS_DONE
        self.put()

    def cancel(self):
        self.status = STATUS_CANCELLED
        self.put()

    def dict(self):
        return {
            "id": str(self.key.id()),
            "text": self.text,
            "start": timestamp(self.start),
            "image_url": self.image_url if self.image_url else None
        }


class Deposit(ndb.Model):
    source = ndb.StringProperty(required=True)
    amount = ndb.IntegerProperty(required=True)  # в рублях


class JsonStorage(ndb.Model):
    data = ndb.JsonProperty()

    @classmethod
    def get(cls, storage_id):
        entity = cls.get_by_id(storage_id)
        if entity:
            return entity.data
        return None

    @classmethod
    def save(cls, storage_id, data):
        if data is None:
            cls.delete(storage_id)
        else:
            cls(id=storage_id, data=data).put()

    @classmethod
    def delete(cls, storage_id):
        ndb.Key(cls, storage_id).delete()