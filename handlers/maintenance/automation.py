__author__ = 'dvpermyakov'

from base import BaseHandler


class AutomationMainHandler(BaseHandler):
    def get(self):
        self.render('/automation.html')