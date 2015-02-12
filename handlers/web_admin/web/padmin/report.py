__author__ = 'dvpermyakov'

from ..base import BaseHandler
from methods import auth
from datetime import datetime
from google.appengine.api import memcache
import urllib
import logging


def redirect(self, url, values):
    params = {
        'blocked': 'true',
        'selected_year': datetime.now().year,
        'selected_month': datetime.now().month,
        'selected_day': datetime.now().day
    }
    params.update(values)
    url = '%s?%s' % (url, urllib.urlencode(params))
    self.redirect(url)


class ReportHandler(BaseHandler):
    @auth.padmin_user_required
    def get(self):
        return self.render('/mt/private_office/report.html')


class ClientsReportHandler(BaseHandler):

    @auth.padmin_user_required
    def get(self):
        chosen_year = self.request.get("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        values = {
            'selected_venue': self.user.venue.id()
        }
        if chosen_year:
            values.update({
                'selected_year': int(chosen_year),
                'selected_month': chosen_month,
                'selected_day': chosen_day
            })
        html = memcache.get('%s:%s:%s:%s:%s' % ('clients', self.user.venue.id(), chosen_year, chosen_month, chosen_day))
        logging.info('%s:%s:%s:%s:%s' % ('clients', self.user.venue.id(), chosen_year, chosen_month, chosen_day))
        logging.info(html)
        if blocked:
            self.response.write(html)
        else:
            redirect(self, '/mt/report/clients', values)