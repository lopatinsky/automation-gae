import hmac
import json
from hashlib import sha1
from urllib import urlencode

import requests
from google.appengine.api import urlfetch

from models.config import config
from models.platius import PlatiusClient

BASE_URL = 'https://iiko.net:9900/api/mobile/v2/'


def _sign_request(secret_key, string):
    hashed = hmac.new(secret_key, string, sha1)
    return hashed.hexdigest()


def _request(endpoint, method, client, query=None, body=None):
    assert isinstance(client, PlatiusClient)
    url = BASE_URL + endpoint
    if query:
        url = "%s?%s" % (url, urlencode(query))
    payload = json.dumps(body) if body is not None else ""

    headers = {
        'Content-Type': 'application/json',
        'AppKey': config.PLATIUS_WHITE_LABEL_MODULE.app_key,
    }
    if client:
        headers['ClientSignature'] = _sign_request(client.token, url + payload)

    res = urlfetch.fetch(url, payload, method, headers)
    if res.status_code != 200:
        raise Exception(res)
    return json.loads(res.content)


def send_sms(user_phone, culture_code='ru-RU'):
    return _request('auth/sendSms', 'POST', None, {
        'userPhone': user_phone,
        'culture': culture_code
    })


def check_sms(user_phone, sms_password, culture_code='ru-RU'):
    return _request('auth/checkSms', 'POST', None, {
        'userPhone': user_phone,
        'password': sms_password,
        'culture': culture_code
    })


def get_user_bar_code(client):
    endpoint = 'user/{}/barcode'.format(client.user_id)
    return _request(endpoint, 'GET', client)


def get_user_info(client):
    endpoint = 'user/{}'.format(client.user_id)
    return _request(endpoint, 'GET', client)


def generate_bar_code(number):
    import barcode
    EAN = barcode.get_barcode_class('ean13')

    from barcode.writer import ImageWriter
    ean = EAN(str(number), writer=ImageWriter())
    ean.save('barcode')
