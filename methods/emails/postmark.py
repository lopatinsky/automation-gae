import json
import logging
from google.appengine.api import urlfetch

__author__ = 'dvpermyakov'

URL = 'https://api.postmarkapp.com/email'


def send_email(from_email, to_email, subject, body, cc_email=None):
    if isinstance(to_email, list):
        to_email = ','.join(to_email)
    payloads = {
        'From': 'noreply-order@ru-beacon.ru',
        'To': to_email,
        'Subject': subject,
        'HtmlBody': body,
        'TrackOpens': False
    }
    if cc_email:
        if isinstance(cc_email, list):
            cc_email = ','.join(cc_email)
        payloads['Cc'] = cc_email
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Postmark-Server-Token': '8d2f261d-21ae-46e1-af97-f850719eb71e'
    }
    response = urlfetch.fetch(URL, payload=json.dumps(payloads), headers=headers, method='POST')
    logging.info(response.status_code)
    logging.info(response.content)
    return response.content
