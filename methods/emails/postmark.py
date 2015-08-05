import json
import logging
from google.appengine.api import urlfetch

__author__ = 'dvpermyakov'

URL = 'https://api.postmarkapp.com/email'


def send_email(from_email, to_email, subject, body):
    payloads = {
        'From': 'noreply-order@ru-beacon.ru',
        'To': to_email,
        'Subject': subject,
        'HtmlBody': body,
        'TrackOpens': False
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Postmark-Server-Token': '8d2f261d-21ae-46e1-af97-f850719eb71e'
    }
    response = urlfetch.fetch(URL, payload=json.dumps(payloads), headers=headers, method='POST')
    logging.info(response.status_code)
    logging.info(response.content)
    return response.content
