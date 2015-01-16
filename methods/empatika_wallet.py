import json
import urllib
from google.appengine.api import urlfetch
from config import config

WALLET_BASE_URL = "http://empatika-wallet.appspot.com/api"


class EmpatikaWalletError(Exception):
    pass


def _get(api_path):
    url = WALLET_BASE_URL + api_path + "?key=" + config.PROMOS_API_KEY
    result = urlfetch.fetch(url)
    response = json.loads(result.content)
    if response["status"] != 200:
        raise EmpatikaWalletError(response["error"])
    return response["data"]


def _post(api_path, params):
    url = WALLET_BASE_URL + api_path + "?key=" + config.PROMOS_API_KEY
    payload = urllib.urlencode(params)
    result = urlfetch.fetch(url, payload, urlfetch.POST,
                            {"Content-Type": "application/x-www-form-urlencoded"})
    response = json.loads(result.content)
    if response["status"] != 200:
        raise EmpatikaWalletError(response["error"])
    return response["data"]


def pay(client_id, order_id, amount):
    api_path = "/pay"
    params = {
        "client_id": client_id,
        "order_id": order_id,
        "amount": amount
    }
    return _post(api_path, params)


def reverse(client_id, order_id):
    api_path = "/reverse"
    params = {
        "client_id": client_id,
        "order_id": order_id
    }
    return _post(api_path, params)


def deposit(client_id, amount, source):
    api_path = "/deposit"
    params = {
        "client_id": client_id,
        "amount": amount,
        "source": source
    }
    return _post(api_path, params)


def get_balance(client_id):
    api_path = "/users/%s/balance" % client_id
    return _get(api_path)["balance"]
