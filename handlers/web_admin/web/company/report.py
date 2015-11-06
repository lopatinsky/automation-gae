from google.appengine.ext.ndb import metadata
from handlers.maintenance.report import get_standart_params
from methods.auth import report_rights_required
from base import CompanyBaseHandler
from methods.report import clients, menu_items, orders, companies


class ReportHandler(CompanyBaseHandler):
    @report_rights_required
    def get(self):
        return self.render('/reports/main.html')


class ClientsReportHandler(CompanyBaseHandler):
    @report_rights_required
    def get(self):
        html_values = clients.get(**get_standart_params(self.request))
        self.render_report('clients', html_values)


class MenuItemsReportHandler(CompanyBaseHandler):
    @report_rights_required
    def get(self):
        html_values = menu_items.get(**get_standart_params(self.request))
        self.render_report('menu_items', html_values)


class OrdersReportHandler(CompanyBaseHandler):
    @report_rights_required
    def get(self):
        html_values = orders.get(lite=self.request.get('lite') == 'on',
                                 **get_standart_params(self.request))
        self.render_report('orders', html_values)


class CompaniesReportHandler(CompanyBaseHandler):
    @report_rights_required
    def get(self):
        if self.user.namespace:
            self.abort(403)
        chosen_namespaces = []
        for namespace in metadata.get_namespaces():
            if self.request.get(namespace):
                chosen_namespaces.append(namespace)
        html_values = companies.get(**get_standart_params(self.request, {
            'chosen_object_type': self.request.get("selected_object_type"),
            'chosen_namespaces': chosen_namespaces
        }, delete_params=['venue_id']))
        self.render_report('companies', html_values)
