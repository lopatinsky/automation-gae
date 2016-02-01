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
        return result, result.phone == client.tel

    @classmethod
    def create_or_overwrite(cls, client):
        result = cls.get_for_client(client)
        if result:
            result.phone = client.tel
        else:
            result = cls(client=client, phone=client.tel)
        result.put()
        return result
