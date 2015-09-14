import json
import logging

from google.appengine.api import urlfetch

from methods.emails import admins
from models.config.config import Config

SMSPILOT_API_KEY = 'YMO7263H170NDGPX2N3863D17EX88HX9P96MFK5O4DKKBQ8D9J897J9O6TQH8741'


def send_sms(to, text):
    config = Config.get()
    text += u'\n%s' % config.APP_NAME
    data = {
        'apikey': SMSPILOT_API_KEY,
        'send': [
            {
                'from': 'Ru-beacon',
                'to': phone,
                'text': text
            } for phone in to
        ]
    }
    response = urlfetch.fetch("http://smspilot.ru/api2.php", payload=json.dumps(data), method='POST',
                              headers={'Content-Type': 'application/json'}).content
    logging.info(response)
    result = json.loads(response)

    success = "send" in result
    for message in result.get("send", []):
        if message["status"] != "0":
            success = False
    if not success:
        admins.send_error("sms", "SMS failure", response)
    return json.loads(response)
