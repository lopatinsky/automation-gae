from google.appengine.ext import ndb
from methods.rendering import timestamp
from models.client import Client

SMS_SUCCESS = 1
SMS_PASSIVE = 2
SMS_CHOICES = [SMS_SUCCESS, SMS_PASSIVE]

VENUE_CHANNEL = 'venue_%s'
CATEGORY_CHANNEL = 'category_%s'

STATUS_CREATED = 0
STATUS_PUSHED = 1
STATUS_CANCELLED = 2
PUSH_STATUS_CHOICES = [STATUS_CREATED, STATUS_PUSHED, STATUS_CANCELLED]


class Channel(ndb.Model):
    name = ndb.StringProperty(required=True)
    channel = ndb.StringProperty(required=True)


class Notification(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.IntegerProperty(choices=PUSH_STATUS_CHOICES, default=STATUS_CREATED)
    start = ndb.DateTimeProperty(required=True)
    text = ndb.StringProperty(required=True)
    popup_text = ndb.StringProperty()
    header = ndb.StringProperty()  # it is used for Android
    channels = ndb.LocalStructuredProperty(Channel, repeated=True)

    def closed(self):
        self.status = STATUS_PUSHED
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
    image_url = ndb.StringProperty(required=True, indexed=False)
    active = ndb.BooleanProperty(required=True, default=False)

    def activate(self):
        self.active = True
        self.put()

    def deactivate(self):
        self.active = False
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