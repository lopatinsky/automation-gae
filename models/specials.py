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
    text = ndb.StringProperty(required=True, indexed=False)
    image_url = ndb.StringProperty(required=True, indexed=False)
    active = ndb.BooleanProperty(required=True, default=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    def dict(self):
        dct = {
            "id": self.key.id(),
            "text": self.text,
            "created_at": timestamp(self.created_at)
        }
        if self.image_url:
            dct["image_url"] = self.image_url
        return dct


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