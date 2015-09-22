import json
import logging

from google.appengine.api import urlfetch

from models.config.config import config
from methods import paypalrestsdk
from methods.paypalrestsdk.payments import Authorization


def get_refresh_token(auth_code):
    return config.PAYPAL_API.get_refresh_token(auth_code)


def get_user_info(refresh_token):
    access_token = config.PAYPAL_API.get_access_token(refresh_token=refresh_token)
    paypal_base_url = "https://api.sandbox.paypal.com" if config.PAYPAL_SANDBOX else "https://api.paypal.com"
    url = paypal_base_url + "/v1/identity/openidconnect/userinfo/?schema=openid"

    logging.info("url: %s", url)
    logging.info("token: %s", access_token)

    result = urlfetch.fetch(url, headers={"Authorization": "Bearer %s" % access_token})
    logging.info(result.content)
    return json.loads(result.content)


def authorize(order_id, amount, refresh_token, correlation_id):
    payment = paypalrestsdk.Payment({
        "intent": "authorize",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [
            {
                "amount": {
                    "total": "%.2f" % amount,
                    "currency": "RUB"
                },
                "description": "Order %s" % order_id
            }
        ],
        "redirect_urls": {
            "return_url": 'http://doubleb-automation-production.appspot.com',  # todo: replace this!
            "cancel_url": 'http://doubleb-automation-production.appspot.com'   # todo: replace this!
        }
    }, api=config.PAYPAL_API)
    if payment.create(refresh_token, correlation_id):
        logging.info(payment)
        return True, payment['transactions'][0]['related_resources'][0]['authorization']['id']
    logging.info(payment.error)
    return False, payment.error


def void(authorization_id):
    auth = Authorization.find(authorization_id, api=config.PAYPAL_API)
    if auth.void():
        return True, None
    return False, auth.error


def capture(authorization_id, amount):
    auth = Authorization.find(authorization_id, api=config.PAYPAL_API)
    capture_obj = auth.capture({
        "amount": {
            "total": "%.2f" % amount,
            "currency": "RUB"
        },
        "is_final_capture": True
    })
    if capture_obj.success():
        return True, None
    return False, capture_obj.error
