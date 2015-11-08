from google.appengine.ext import ndb
from models.proxy.unified_app import ProxyCity

__author__ = 'dvpermyakov'


def save_city(client, city_id):
    if city_id and client.city and client.city.id() != city_id:
        client.city = ndb.Key(ProxyCity, city_id)
        client.put()
