# coding=utf-8
from collections import Counter
from datetime import datetime, timedelta
from models.order import STATUS_MAP
from models.payment_types import PAYMENT_TYPE_MAP
from report_methods import suitable_date, PROJECT_STARTING_YEAR
from models import Order, Client, Venue


def _order_data(order):
    venue = Venue.get_by_id(order.venue_id)
    dct = {
        "order_id": order.key.id(),
        "status": STATUS_MAP[order.status],
        "date": (order.date_created + timedelta(hours=venue.timezone_offset)).strftime("%d.%m.%Y"),
        "created_time": (order.date_created + timedelta(hours=venue.timezone_offset)).strftime("%H:%M:%S"),
        "delivery_time": (order.delivery_time + timedelta(hours=venue.timezone_offset)).strftime("%H:%M:%S"),
        "payment_type": PAYMENT_TYPE_MAP[order.payment_type_id],
        "total_sum": order.total_sum if order.payment_type_id != 666 else 0,
        "venue_revenue": sum(d.revenue for d in order.item_details),
        "venue": venue.title,
        "items": []
    }
    client = Client.get_by_id(order.client_id)
    dct["client"] = {
        "id": client.key.id(),
        "name": client.name,
        "surname": client.surname,
        "phone": client.tel
    }
    for item_key, count in Counter(order.items).items():
        item = item_key.get()
        dct["items"].append({
            "title": item.title,
            "price": item.price,
            "quantity": count
        })
    return dct


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

    if chosen_day:
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

    values = {
        'venues': Venue.query().fetch(),
        'orders': order_dicts,
        'start_year': PROJECT_STARTING_YEAR,
        'end_year': datetime.now().year,
        'chosen_venue': venue_id,
        'chosen_year': chosen_year,
        'chosen_month': chosen_month,
        'chosen_day': chosen_day
    }
    return values
