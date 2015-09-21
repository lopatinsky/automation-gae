from handlers.maintenance.report import get_standart_params
from methods.auth import check_rights_decorator
from base import CompanyBaseHandler
from methods.report import clients, menu_items, orders
from models.user import CompanyUser


_check_rights = check_rights_decorator((CompanyUser.RIGHTS_BIT_REPORT,))


class ReportHandler(CompanyBaseHandler):
    @_check_rights
    def get(self):
        return self.render('/reports/main.html')


class ClientsReportHandler(CompanyBaseHandler):
    @_check_rights
    def get(self):
        html_values = clients.get(**get_standart_params(self.request))
        self.render_report('clients', html_values)


class MenuItemsReportHandler(CompanyBaseHandler):
    @_check_rights
    def get(self):
        html_values = menu_items.get(**get_standart_params(self.request))
        self.render_report('menu_items', html_values)


class OrdersReportHandler(CompanyBaseHandler):
    @_check_rights
    def get(self):
        html_values = orders.get(**get_standart_params(self.request))
        self.render_report('orders', html_values)
