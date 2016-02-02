from google.appengine.ext import ndb

from models.client import Client


class PlatiusClient(ndb.Model):
    client = ndb.KeyProperty(Client, required=True)
    phone = ndb.StringProperty(required=True)
    user_id = ndb.StringProperty(required=True)
    token = ndb.StringProperty(required=True)

    @classmethod
    def get_for_client(cls, client):
        return cls.query(cls.client == client.key).get()

    @classmethod
    def get_and_validate(cls, client):
        result = cls.get_for_client(client)
        valid = result is not None and result.phone == client.tel
        return result, valid

    @classmethod
    def create_or_overwrite(cls, client, user_id, token):
        result = cls.get_for_client(client)
        if not result:
            result = cls(client=client.key)
        result.populate(phone=client.tel, user_id=user_id, token=token)
        result.put()
        return result
