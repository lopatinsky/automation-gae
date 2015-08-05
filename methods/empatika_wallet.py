import json
import logging
import urllib
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch_errors import DeadlineExceededError
from config import config
from google.appengine.api import memcache

WALLET_BASE_URL = "http://empatika-wallet.appspot.com/api"


class EmpatikaWalletError(Exception):
    pass


def _get(api_path):
    url = WALLET_BASE_URL + api_path + "?key=" + config.WALLET_API_KEY
    logging.debug(url)
    result = urlfetch.fetch(url)
    logging.info(result.content)
    response = json.loads(result.content)
    if response["status"] != 200:
        raise EmpatikaWalletError(response["error"])
    return response["data"]


def _post(api_path, params, deadline=None):
    url = WALLET_BASE_URL + api_path + "?key=" + config.WALLET_API_KEY
    payload = urllib.urlencode(params)
    logging.debug(url)
    logging.debug(payload)
    result = urlfetch.fetch(url, payload, urlfetch.POST,
                            {"Content-Type": "application/x-www-form-urlencoded"},
                            deadline=deadline)
    logging.info(result.content)
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
    return _post(api_path, params, deadline=60)


def reverse(client_id, order_id):
    api_path = "/reverse"
    params = {
        "client_id": client_id,
        "order_id": order_id
    }
    return _post(api_path, params, deadline=60)


def deposit(client_id, amount, source):
    api_path = "/deposit"
    params = {
        "client_id": client_id,
        "amount": amount,
        "source": source
    }
    return _post(api_path, params, deadline=60)


def deposit_history(sources):
    api_path = "/deposit_history"
    params = {
        "request": json.dumps({
            'sources': sources
        })
    }
    return _post(api_path, params)


def get_balance(client_id, from_memcache=False, set_zero_if_fail=False, raise_error=False):
    api_path = "/clients/%s/balance" % client_id
    cache_key = 'user_wallet_balance_%s' % client_id
    balance = None
    if from_memcache:
        balance = memcache.get(cache_key)
    if balance is None:
        try:
            balance = _get(api_path)['balance']
            memcache.set(cache_key, balance, time=60)
        except DeadlineExceededError:
            if set_zero_if_fail:
                balance = 0
            if raise_error:
                raise Exception('Raising error in get wallet balance')
    return balance
