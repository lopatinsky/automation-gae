__author__ = 'dvpermyakov'

from ..base import BaseHandler
from methods import auth
from methods import excel
from methods.report import clients, menu_items, orders


def get_standart_params(request, user, values=None, delete_params=None):
    params = {
        'venue_id': user.venue.id(),
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


class ReportHandler(BaseHandler):
    @auth.padmin_user_required
    def get(self):
        return self.render('/mt/private_office/report.html', padmin=self.user)


class ClientsReportHandler(BaseHandler):
    @auth.padmin_user_required
    def get(self):
        html_values = clients.get(**get_standart_params(self.request, self.user))
        html_values['padmin'] = self.user
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'clients', 'reported_clients.html', **html_values)
        else:
            self.render('/mt/reported_clients.html', **html_values)


class MenuItemsReportHandler(BaseHandler):
    @auth.padmin_user_required
    def get(self):
        html_values = menu_items.get(**get_standart_params(self.request, self.user))
        html_values['padmin'] = self.user
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'menu_items', 'reported_menu_items.html', **html_values)
        else:
            self.render('/mt/reported_menu_items.html', **html_values)


class OrdersReportHandler(BaseHandler):
    @auth.padmin_user_required
    def get(self):
        html_values = orders.get(**get_standart_params(self.request, self.user))
        html_values['padmin'] = self.user
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'oders', 'reported_orders.html', **html_values)
        else:
            self.render('/mt/reported_orders.html', **html_values)