import json
import urllib

from google.appengine.api import urlfetch

from models.config.config import config

PROMOS_BASE_URL = "http://empatika-promos.appspot.com/api"


class EmpatikaPromosError(Exception):
    pass


def _get(api_path):
    url = PROMOS_BASE_URL + api_path + "?key=" + config.PROMOS_API_KEY
    result = urlfetch.fetch(url, deadline=10)
    response = json.loads(result.content)
    if response["status"] != 200:
        raise EmpatikaPromosError(response["error"])
    return response["data"]


def _post(api_path, params):
    url = PROMOS_BASE_URL + api_path + "?key=" + config.PROMOS_API_KEY
    payload = urllib.urlencode(params)
    result = urlfetch.fetch(url, payload, urlfetch.POST,
                            {"Content-Type": "application/x-www-form-urlencoded"}, deadline=10)
    response = json.loads(result.content)
    if response["status"] != 200:
        raise EmpatikaPromosError(response["error"])
    return response["data"]


def get_user_points(user_id):
    api_path = "/users/%s/points" % user_id
    return _get(api_path)["points"]


def register_order(user_id, points, order_id):
    api_path = "/order"
    params = {
        "user_id": user_id,
        "points": points,
        "order_id": order_id
    }
    return _post(api_path, params)


def activate_promo(user_id, promo_id, count):
    api_path = "/promos/%s/activate" % promo_id
    params = {
        "user_id": user_id,
        "count": count
    }
    return _post(api_path, params)


def cancel_activation(activation_id):
    api_path = "/activations/%s/cancel" % activation_id
    return _post(api_path, {})
