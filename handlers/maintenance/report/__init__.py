__author__ = 'dvpermyakov'

from menu_items import MenuItemsReportHandler
from venues import VenuesReportHandler, VenuesReportWithDatesHandler
from clients import ClientsReportHandler
from orders import OrdersReportHandler
from tablet_requests_report import TabletRequestGraphHandler
from report_methods import PROJECT_STARTING_YEAR
from repeated_orders import RepeatedOrdersHandler
from square_table import SquareTableHandler

from ..base import BaseHandler


class ReportHandler(BaseHandler):
    def get(self):
        self.render('report.html')