__author__ = 'dvpermyakov'

from google.appengine.api import urlfetch
import json
import logging

MANDRILL_SEND_EMAIL_URL = 'https://mandrillapp.com/api/1.0/messages/send.json'
API_KEY = 'e02w7UmHBExqLjvFZNTVgA'


def send_email(from_email, to_email, subject, body, recipients=None):
    payload = {
        'key': API_KEY,
        'message': {
            'html': '<p>%s</p>' % body,
            'subject': subject,
            'from_email': from_email,
            'to': [{
                'email': to_email
            }],
            'merge_vars': [{
                'rcpt': ''
            }],
            'tags': [
                'example_tag'
            ]
        }
    }
    if recipients:
        for i, recipient in enumerate(recipients):
            payload['message']['merge_vars'][i]['rcpt'] = recipient
    payload = json.dumps(payload)
    result = urlfetch.fetch(MANDRILL_SEND_EMAIL_URL, payload=payload, method=urlfetch.POST,
                            headers={'Content-Type': 'application/json'})
    logging.info(result.status_code)
    return result.content