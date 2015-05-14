from config import config
from methods import paypalrestsdk
from methods.paypalrestsdk.payments import Authorization


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
        ]
    }, api=config.PAYPAL_API)
    if payment.create(refresh_token, correlation_id):
        return True, payment['transactions'][0]['related_resources'][0]['authorization']['id']
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
