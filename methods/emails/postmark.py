import json
import logging
import smtplib
from email.mime.text import MIMEText

from google.appengine.api import urlfetch

__author__ = 'dvpermyakov'

URL = 'https://api.postmarkapp.com/email'
SMTP_URL = 'smtp.postmarkapp.com'
TOKEN = '56769b86-939a-4204-8555-bcc5d53a63b5'


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
        'X-Postmark-Server-Token': TOKEN
    }
    response = urlfetch.fetch(URL, payload=json.dumps(payloads), headers=headers, method='POST')
    logging.info(response.status_code)
    logging.info(response.content)
    return response.content


def send_by_smtp(from_email, to_email, subject, body, as_html=True):
    message = MIMEText(body, 'html' if as_html else 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = 'noreply-order@ru-beacon.ru'
    message['To'] = to_email
    logging.info(message.as_string())
    smtp = smtplib.SMTP(SMTP_URL, 2525)
    smtp.login(TOKEN, TOKEN)
    smtp.sendmail('noreply-order@ru-beacon.ru', to_email, message.as_string())
    smtp.quit()
