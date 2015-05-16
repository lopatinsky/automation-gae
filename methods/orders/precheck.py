import re
from google.appengine.api import memcache
from models import Order, Client

__author__ = 'dvpermyakov'


def check_order_id(order_id):
    cache_key = "order_%s" % order_id
    if Order.get_by_id(order_id) or not memcache.add(cache_key, 1):
        return False, None
    else:
        return True, cache_key


def set_client_info(client_json):
    client_id = int(client_json.get('id'))
    if not client_id:
        return None, None
    client = Client.get_by_id(client_id)
    if not client:
        return None, None
    name = client_json.get('name').split(None, 1)
    client_name = name[0]
    client_surname = name[1] if len(name) > 1 else ""
    client_tel = re.sub("[^0-9]", "", client_json.get('phone'))
    client_email = client_json.get('email')
    if client.name != client_name or client.surname != client_surname or client.tel != client_tel \
            or client.email != client_email:
        client.name = client_name
        client.surname = client_surname
        client.tel = client_tel
        client.email = client_email
        client.put()
    return client_id, client