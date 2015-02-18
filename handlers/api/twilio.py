#coding:utf-8
__author__ = 'dvpermyakov'

from base import ApiHandler
from methods import email
import logging


class ReceiveSms(ApiHandler):
    def post(self):
        logging.info(self.request.POST)
        country = self.request.get('FromCountry')
        region = self.request.get('FromState')
        phone = self.request.get('From')
        body = self.request.get('Body')
        message = u'Страна: %s\nРегион: %s\nТелефон: %s\nСообщение: %s' % (country, region, phone, body)
        logging.info(message)
        email.send_error('analytics', u'Смс ответ', body=message)