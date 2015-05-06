# coding:utf-8
__author__ = 'dvpermyakov'

from base import BaseHandler
from methods import excel
from methods.report import clients, menu_items, notifications, orders, repeated_orders, square_table, venues,\
    card_binding


def get_standart_params(request, values=None, delete_params=None):
    params = {
        'venue_id': request.get("selected_venue"),
        'chosen_year': request.get_range("selected_year"),
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
    def get(self):
        self.render('/reports/main.html')


class ClientsReportHandler(BaseHandler):
    def get(self):
        html_values = clients.get(**get_standart_params(self.request, {
            'chosen_days': self.request.get_all('selected_day')
        }, delete_params=['chosen_day']))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'clients', 'clients.html', **html_values)
        else:
            self.render('/reports/clients.html', **html_values)


class MenuItemsReportHandler(BaseHandler):
    def get(self):
        html_values = menu_items.get(**get_standart_params(self.request))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'menu_items', 'menu_items.html', **html_values)
        else:
            self.render('/reports/menu_items.html', **html_values)


class VenuesReportHandler(BaseHandler):
    def get(self):
        html_values = venues.get(**get_standart_params(self.request, delete_params=['venue_id']))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'venues', 'venues.html', **html_values)
        else:
            self.render('/reports/venues.html', **html_values)


class VenuesReportWithDatesHandler(BaseHandler):
    def get(self):
        html_values = venues.get_with_dates(**get_standart_params(self.request, delete_params=['venue_id', 'chosen_day']))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'venues_with_dates', 'venues_with_dates.html', **html_values)
        else:
            self.render('/reports/venues_with_dates.html', **html_values)


class OrdersReportHandler(BaseHandler):
    def get(self):
        html_values = orders.get(**get_standart_params(self.request, {
            'chosen_days': self.request.get_all('selected_day'),
        }, delete_params=['chosen_day']))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'oders', 'orders.html', **html_values)
        else:
            self.render('/reports/orders.html', **html_values)


class RepeatedOrdersHandler(BaseHandler):
    def get(self):
        html_values = repeated_orders.get(**get_standart_params(self.request, delete_params=['venue_id', 'chosen_day']))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'repeated_oders', 'repeated_orders.html', **html_values)
        else:
            self.render('/reports/repeated_orders.html', **html_values)


class SquareTableHandler(BaseHandler):
    def get(self):
        square = square_table.get()
        if not square:
            self.response.write("Report not ready")
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'square_table', 'square_table.html', square=square)
        else:
            self.render('/reports/square_table.html', square=square)


class NotificationsReportHandler(BaseHandler):
    def get(self):
        html_values = notifications.get(**get_standart_params(self.request, {
            'chosen_type': self.request.get('selected_type')
        }, delete_params=['venue_id', 'chosen_day']))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'repeated_notification', 'notification.html', **html_values)
        else:
            self.render('/reports/notification.html', **html_values)


class CardBindingReportHandler(BaseHandler):
    def get(self):
        html_values = card_binding.get(**get_standart_params(self.request, {
            'chosen_year': self.request.get_range("selected_year"),
            'chosen_type': self.request.get_range("selected_type"),
            'client_id': self.request.get("client_id"),
            'chosen_days': self.request.get_all('selected_day'),
        }, delete_params=['chosen_day', 'venue_id']))
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, 'card_binding', 'card_binding.html', **html_values)
        else:
            self.render('/reports/card_binding.html', **html_values)
