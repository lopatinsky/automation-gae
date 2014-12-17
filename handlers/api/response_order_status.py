__author__ = 'dvpermyakov'

import webapp2
from models import OrderNotificationStatus
from .base import ApiHandler


class CheckOrderSuccessHandler(webapp2.RequestHandler):
    def post(self):
        status_id = self.request.get('status_id')
        status = OrderNotificationStatus.get_by_id(status_id)
        if not status.response_success:
            pass


class ClientSettingSuccessHandler(ApiHandler):
    def post(self):
        status_id = self.request.get('status_id')
        status = OrderNotificationStatus.get_by_id(status_id)
        status.response_success = True