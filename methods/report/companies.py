from datetime import datetime

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata

from models.config.config import Config
from methods.report.report_methods import suitable_date, PROJECT_STARTING_YEAR
from models import Order
from models.order import STATUS_MAP, READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER
from models.payment_types import PAYMENT_TYPE_MAP

__author__ = 'dvpermyakov'


class Company:
    def __init__(self, namespace, name, in_production):
        self.namespace = namespace
        self.name = name
        self.payments = []
        self.info = {}
        self.in_production = in_production


def get(chosen_year, chosen_month, chosen_day, chosen_object_type, chosen_namespaces):
    if not chosen_namespaces:
        chosen_year = datetime.now().year
        chosen_month = datetime.now().month
        chosen_day = datetime.now().day
        chosen_object_type = '0'
    companies = []
    skip_companies = []
    for namespace in metadata.get_namespaces():
        namespace_manager.set_namespace(namespace)
        config = Config.get()
        if not config or not config.APP_NAME:
            continue
        if (chosen_namespaces and namespace in chosen_namespaces) or \
                (not chosen_namespaces and config.IN_PRODUCTION):
            companies.append(Company(namespace, config.APP_NAME, config.IN_PRODUCTION))
        else:
            skip_companies.append(Company(namespace, config.APP_NAME, config.IN_PRODUCTION))
    if not chosen_namespaces:
        chosen_namespaces = [c.namespace for c in companies]
    start = suitable_date(chosen_day, chosen_month, chosen_year, True)
    end = suitable_date(chosen_day, chosen_month, chosen_year, False)
    statuses = (READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER)  # it can be tunable
    total = {
        'orders_number': 0,
        'orders_sum': 0,
        'average_orders_sum': 0
    }
    for company in companies:
        namespace_manager.set_namespace(company.namespace)
        orders = Order.query(Order.date_created >= start, Order.date_created <= end).fetch()
        for order in orders:
            if order.payment_type_id not in [payment['type'] for payment in company.payments]:
                company.payments.append({
                    'type': order.payment_type_id,
                    'name': PAYMENT_TYPE_MAP[order.payment_type_id]
                })
                company.info[order.payment_type_id] = {}
                for status in statuses:
                    company.info[order.payment_type_id][status] = {}
                    company.info[order.payment_type_id][status]["client_ids"] = []
                    company.info[order.payment_type_id][status]["orders_number"] = 0
                    company.info[order.payment_type_id][status]["goods_number"] = 0
                    company.info[order.payment_type_id][status]["orders_sum"] = 0
            if order.status in statuses:
                if order.client_id not in company.info[order.payment_type_id][order.status]["client_ids"]:
                    company.info[order.payment_type_id][order.status]["client_ids"].append(order.client_id)
                company.info[order.payment_type_id][order.status]["orders_number"] += 1
                company.info[order.payment_type_id][order.status]["goods_number"] += len(order.item_details)
                company.info[order.payment_type_id][order.status]["orders_sum"] += order.total_sum - order.wallet_payment
        for payment in company.payments:
            for status in statuses:
                company.info[payment['type']][status]["client_number"] = len(company.info[payment['type']][status]["client_ids"])
                company.info[payment['type']][status]["average_orders_sum"] = \
                    company.info[payment['type']][status]["orders_sum"] / company.info[payment['type']][status]["orders_number"]\
                        if company.info[payment['type']][status]["orders_number"] else 0
                company.info[payment['type']][status]["orders_sum"] = round(company.info[payment['type']][status]["orders_sum"], 2)
                company.info[payment['type']][status]["average_orders_sum"] = round(company.info[payment['type']][status]["average_orders_sum"], 2)
        company.payments = sorted(company.payments, key=lambda payment: payment['type'])
        total['orders_number'] += sum([company.info[payment['type']][READY_ORDER]['orders_number']
                                       for payment in company.payments])
        total['orders_sum'] += sum([company.info[payment['type']][READY_ORDER]['orders_sum']
                                    for payment in company.payments])

    total['average_orders_sum'] = round(total['orders_sum'] / total['orders_number'], 2) if total['orders_number'] else 0

    companies.extend(skip_companies)
    return {
        'companies': companies,
        'chosen_namespaces': chosen_namespaces,
        'statuses': statuses,
        'status_map': STATUS_MAP,
        'start_year': PROJECT_STARTING_YEAR,
        'end_year': datetime.now().year,
        'chosen_year': chosen_year,
        'chosen_month': chosen_month,
        'chosen_day': chosen_day,
        'chosen_object_type': chosen_object_type,
        'total': total
    }