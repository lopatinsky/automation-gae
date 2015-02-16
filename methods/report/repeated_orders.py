__author__ = 'dvpermyakov'

from models import Order, Client, READY_ORDER
from report_methods import suitable_date, PROJECT_STARTING_YEAR
import calendar
from datetime import datetime


def get(chosen_year, chosen_month):
    if not chosen_year:
        chosen_year = datetime.now().year
        chosen_month = datetime.now().month
    else:
        chosen_year = int(chosen_year)
    days = []
    total = {
        'new_number': 0,
        'old_number': 0,
        'new_sum': 0,
        'old_sum': 0
    }

    first_mapping = {}

    def _get_first_order(client_id):
        if client_id not in first_mapping:
            first_mapping[client_id] = Order.query(Order.client_id == client_id, Order.status == READY_ORDER)\
                .order(Order.date_created).get(keys_only=True)
        return first_mapping[client_id]

    for day in range(1, calendar.monthrange(chosen_year, chosen_month)[1] + 1):
        new_number = 0
        old_number = 0
        new_sum = 0
        old_sum = 0
        query = Order.query(Order.date_created >= suitable_date(day, chosen_month, chosen_year, True))
        query = query.filter(Order.date_created <= suitable_date(day, chosen_month, chosen_year, False))
        for order in query.fetch():
            if order.status != READY_ORDER:
                continue
            client = Client.get_by_id(order.client_id)
            first_order_key = _get_first_order(client.key.id())
            if first_order_key.id() == order.key.id():
                new_number += 1
                new_sum += order.total_sum
            else:
                old_number += 1
                old_sum += order.total_sum
        days.append({
            'day': day,
            'new_number': new_number,
            'old_number': old_number,
            'new_sum': new_sum,
            'old_sum': old_sum
        })
        total['new_number'] += new_number
        total['old_number'] += old_number
        total['new_sum'] += new_sum
        total['old_sum'] += old_sum

    values = {
        'days': days,
        'total': total,
        'start_year': PROJECT_STARTING_YEAR,
        'end_year': datetime.now().year,
        'chosen_year': chosen_year,
        'chosen_month': chosen_month,
    }
    return values