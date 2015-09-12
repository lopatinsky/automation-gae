# coding:utf-8
from datetime import datetime, timedelta, date, time
from google.appengine.ext.ndb import metadata

__author__ = 'dvpermyakov'

from base import BaseHandler
from methods import excel
from methods.report import clients, menu_items, notifications, orders, repeated_orders, square_table, venues,\
    card_binding, companies


def get_standart_params(request, values=None, delete_params=None):
    params = {
        'venue_id': request.get("selected_venue"),
    }
    try:
        params["start"] = datetime.strptime(request.get("start"), "%Y-%m-%d")
        params["end"] = datetime.strptime(request.get("end"), "%Y-%m-%d")
    except ValueError:
        params["start"] = params["end"] = datetime.combine(date.today(), time())
    params["end"] = params["end"] + timedelta(days=1) - timedelta(microseconds=1)
    if delete_params:
        for param in delete_params:
            del params[param]
    if values:
        params.update(values)
    return params


class ReportHandler(BaseHandler):
    def get(self):
        self.render('/reports/main.html')


class BaseReportHandler(BaseHandler):
    def render_report(self, report_name, html_values):
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, report_name, report_name + '.html', **html_values)
        else:
            self.render('/reports/%s.html' % report_name, **html_values)


class ClientsReportHandler(BaseReportHandler):
    def get(self):
        html_values = clients.get(**get_standart_params(self.request))
        self.render_report('clients', html_values)


class MenuItemsReportHandler(BaseReportHandler):
    def get(self):
        html_values = menu_items.get(**get_standart_params(self.request))
        self.render_report('menu_items', html_values)


class VenuesReportHandler(BaseReportHandler):
    def get(self):
        html_values = venues.get(**get_standart_params(self.request, delete_params=['venue_id']))
        self.render_report('venues', html_values)


class VenuesReportWithDatesHandler(BaseReportHandler):
    def get(self):
        html_values = venues.get_with_dates(**get_standart_params(self.request, delete_params=['venue_id', 'chosen_day']))
        self.render_report('venues_with_dates', html_values)


class OrdersReportHandler(BaseReportHandler):
    def get(self):
        html_values = orders.get(**get_standart_params(self.request))
        self.render_report('orders', html_values)


class RepeatedOrdersHandler(BaseReportHandler):
    def get(self):
        html_values = repeated_orders.get(**get_standart_params(self.request, delete_params=['venue_id', 'chosen_day']))
        self.render_report('repeated_orders', html_values)


class SquareTableHandler(BaseReportHandler):
    def get(self):
        square = square_table.get()
        if not square:
            self.response.write("Report not ready")
        self.render_report('square_table', square)


class NotificationsReportHandler(BaseReportHandler):
    def get(self):
        html_values = notifications.get(**get_standart_params(self.request, {
            'chosen_type': self.request.get('selected_type')
        }, delete_params=['venue_id', 'chosen_day']))
        self.render_report('notification', html_values)


class CardBindingReportHandler(BaseReportHandler):
    def get(self):
        html_values = card_binding.get(**get_standart_params(self.request, {
            'chosen_year': self.request.get_range("selected_year"),
            'chosen_type': self.request.get_range("selected_type"),
            'client_id': self.request.get("client_id"),
            'chosen_days': self.request.get_all('selected_day'),
        }, delete_params=['chosen_day', 'venue_id']))
        self.render_report('card_binding', html_values)


class CompaniesReportHandler(BaseReportHandler):
    def get(self):
        chosen_namespaces = []
        for namespace in metadata.get_namespaces():
            if self.request.get(namespace):
                chosen_namespaces.append(namespace)
        html_values = companies.get(**get_standart_params(self.request, {
            'chosen_object_type': self.request.get("selected_object_type"),
            'chosen_namespaces': chosen_namespaces
        }, delete_params=['venue_id']))
        self.render_report('companies', html_values)
