from handlers.maintenance.report import get_standart_params
from methods.auth import company_user_required
from base import CompanyBaseHandler
from methods.report import clients, menu_items, orders


class ReportHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        return self.render('/reports/main.html')


class ClientsReportHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        html_values = clients.get(**get_standart_params(self.request))
        self.render_report('clients', html_values)


class MenuItemsReportHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        html_values = menu_items.get(**get_standart_params(self.request))
        self.render_report('menu_items', html_values)


class OrdersReportHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        html_values = orders.get(**get_standart_params(self.request))
        self.render_report('orders', html_values)
