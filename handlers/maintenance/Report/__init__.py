__author__ = 'dvpermyakov'

from menu_items import MenuItemsReportHandler
from venues import VenuesReportHandler
from clients import ClientsReportHandler
from methods import PROJECT_STARTING_YEAR

from ..base import BaseHandler


class ReportHandler(BaseHandler):
    def get(self):
        self.render('report.html')