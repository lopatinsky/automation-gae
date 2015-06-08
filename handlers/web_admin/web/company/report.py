from methods.auth import company_user_required
from base import CompanyBaseHandler
from methods import excel
from methods.report import clients, menu_items, orders


def get_standart_params(request, values=None, delete_params=None):
    params = {
        'venue_id': request.get("selected_venue"),
        'chosen_year': request.get("selected_year"),
        'chosen_month': request.get_range("selected_month"),
        'chosen_day': request.get_range("selected_day"),
    }
    if delete_params:
        for param in delete_params:
            del params[param]
    if values:
        params.update(values)
    return params


class ReportHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        return self.render('/reports/main.html')


class ClientsReportHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        html_values = clients.get(**get_standart_params(self.request))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'clients', 'clients.html', **html_values)
        else:
            return self.report_render('/clients.html', **html_values)


class MenuItemsReportHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        html_values = menu_items.get(**get_standart_params(self.request))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'menu_items', 'menu_items.html', **html_values)
        else:
            return self.report_render('/menu_items.html', **html_values)


class OrdersReportHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        html_values = orders.get(**get_standart_params(self.request))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'oders', 'orders.html', **html_values)
        else:
            return self.report_render('/orders.html', **html_values)