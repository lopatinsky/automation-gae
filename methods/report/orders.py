# coding=utf-8
from collections import Counter
from datetime import datetime, timedelta
from config import config
from models.order import STATUS_MAP, READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER
from models.payment_types import PAYMENT_TYPE_MAP, CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE
from report_methods import suitable_date, PROJECT_STARTING_YEAR
from models import Order, Client, Venue


def _order_data(order):
    venue = Venue.get_by_id(order.venue_id)
    dct = {
        "order_id": order.key.id(),
        "comment": order.comment if order.comment else '',
        "return_comment": order.return_comment if order.return_comment else '',
        "status": STATUS_MAP[order.status],
        "date": (order.date_created + timedelta(hours=venue.timezone_offset)).strftime("%d.%m.%Y"),
        "created_time": (order.date_created + timedelta(hours=venue.timezone_offset)).strftime("%H:%M:%S"),
        "delivery_time": (order.delivery_time + timedelta(hours=venue.timezone_offset)).strftime("%H:%M:%S"),
        "payment_type": PAYMENT_TYPE_MAP[order.payment_type_id],
        "total_sum_without_promos": sum(d.price / 100.0 for d in order.item_details),
        "total_sum_with_promos_without_wallet": order.total_sum - order.wallet_payment,
        "total_sum": order.total_sum,
        "venue_revenue": sum(d.revenue for d in order.item_details),
        "venue": venue.title,
        "items": order.grouped_item_dict(order.item_details)
    }
    client = Client.get_by_id(order.client_id)
    dct["client"] = {
        "id": client.key.id(),
        "name": client.name,
        "surname": client.surname,
        "phone": client.tel
    }
    return dct


def _total(orders, status, payment_type):
    count = 0
    total_sum = 0.0
    total_sum_without_promos = 0.0
    total_payment = 0.0

    for order in orders:
        if (status is not None and order.status != status) or \
                (payment_type is not None and order.payment_type_id != payment_type):
            continue
        count += 1
        total_sum += total_sum
        total_sum_without_promos += sum(d.price / 100.0 for d in order.item_details)
        total_payment += order.total_sum - order.wallet_payment
    return {
        "orders_number": count,
        "status": STATUS_MAP[status] if status is not None else u'Все статусы',
        "payment_type": PAYMENT_TYPE_MAP[payment_type] if payment_type is not None else u'Все способы оплаты',
        "total_sum_without_promos": total_sum_without_promos,
        "total_sum_with_promos_without_wallet": total_payment,
        "total_sum": total_sum
    }

def get(venue_id, chosen_year, chosen_month, chosen_day=None, chosen_days=None):
    if not venue_id:
        venue_id = 0
        chosen_year = datetime.now().year
        chosen_month = datetime.now().month
        chosen_day = datetime.now().day
    else:
        venue_id = int(venue_id)

    if not chosen_year:
        chosen_year = datetime.now().year
        chosen_month = datetime.now().month
        chosen_day = datetime.now().day
    else:
        chosen_year = int(chosen_year)

    if not chosen_year:
        chosen_month = 0
    if not chosen_month:
        chosen_day = 0

    if chosen_day is not None:
        start = suitable_date(chosen_day, chosen_month, chosen_year, True)
        end = suitable_date(chosen_day, chosen_month, chosen_year, False)
    else:
        chosen_days = [int(day) for day in chosen_days]
        min_day = min(chosen_days)
        max_day = max(chosen_days)
        start = suitable_date(min_day, chosen_month, chosen_year, True)
        end = suitable_date(max_day, chosen_month, chosen_year, False)

    query = Order.query(Order.date_created >= start, Order.date_created <= end)
    if venue_id:
        query = query.filter(Order.venue_id == venue_id)
    orders = query.fetch()
    order_dicts = [_order_data(order) for order in orders]

    totals = [
        _total(orders, READY_ORDER, CASH_PAYMENT_TYPE),
        _total(orders, READY_ORDER, CARD_PAYMENT_TYPE),
        _total(orders, READY_ORDER, PAYPAL_PAYMENT_TYPE) if config.PAYPAL_CLIENT_ID else None,
        _total(orders, CANCELED_BY_CLIENT_ORDER, None),
        _total(orders, CANCELED_BY_BARISTA_ORDER, None)
    ]
    totals = filter(None, totals)

    values = {
        'venues': Venue.query().fetch(),
        'orders': order_dicts,
        'start_year': PROJECT_STARTING_YEAR,
        'end_year': datetime.now().year,
        'chosen_venue': venue_id,
        'chosen_year': chosen_year,
        'chosen_month': chosen_month,
        'chosen_day': chosen_day,
        'totals': totals,
    }
    return values
