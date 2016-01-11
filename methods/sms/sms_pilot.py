import json
import logging

from google.appengine.api import urlfetch

from methods.emails import admins
from models.config.config import config

SMSPILOT_API_KEY = 'YMO7263H170NDGPX2N3863D17EX88HX9P96MFK5O4DKKBQ8D9J897J9O6TQH8741'


def send_sms(to, text, company_footer=True):
    if company_footer:
        text += u'\n%s' % config.APP_NAME
    data = {
        'apikey': SMSPILOT_API_KEY,
        'send': [
            {
                'from': 'Ru-beacon',
                'to': phone,
                'text': text
            } for phone in to if phone
        ]
    }
    if not data['send']:
        return
    try:
        response = urlfetch.fetch("http://smspilot.ru/api2.php", payload=json.dumps(data), method='POST',
                                  headers={'Content-Type': 'application/json'}).content
        logging.info(response)
        result = json.loads(response)
        success = "send" in result
        for message in result.get("send", []):
            if message["status"] != "0":
                success = False
    except Exception as e:
        success = False
        response = str(e)
    if not success:
        admins.send_error("sms", "SMS failure", response)
