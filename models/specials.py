from google.appengine.ext import ndb
from methods.rendering import timestamp

PUSH_NOTIFICATION = 0
SMS_SUCCESS = 1
SMS_PASSIVE = 2


class Notification(ndb.Model):
    client_id = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    type = ndb.IntegerProperty(required=True, choices=(PUSH_NOTIFICATION, SMS_SUCCESS, SMS_PASSIVE))


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
            "id": self.key.id(),
            "text": self.text,
            "created": timestamp(self.created),
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