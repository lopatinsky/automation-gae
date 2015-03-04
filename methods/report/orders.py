# coding=utf-8
from collections import Counter
from datetime import datetime
from config import config
from report_methods import suitable_date, PROJECT_STARTING_YEAR
from models import Order, Client, NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER, \
    CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE, BONUS_PAYMENT_TYPE, Venue, CREATING_ORDER
from methods.excel import send_excel_file


_STATUS_STRINGS = {
    NEW_ORDER: u"Новый",
    READY_ORDER: u"Выдан",
    CANCELED_BY_CLIENT_ORDER: u"Отменен клиентом",
    CANCELED_BY_BARISTA_ORDER: u"Отменен бариста",
    CREATING_ORDER: u'СОзданный заказ'
}

_PAYMENT_TYPE_STRINGS = {
    CASH_PAYMENT_TYPE: u"Наличные",
    CARD_PAYMENT_TYPE: u"Карта",
    BONUS_PAYMENT_TYPE: u"Бонусы"
}


def _order_data(order):
    venue = Venue.get_by_id(order.venue_id)
    dct = {
        "order_id": order.key.id(),
        "status": _STATUS_STRINGS[order.status],
        "date": (order.date_created + config.TIMEZONE_OFFSET).strftime("%d.%m.%Y"),
        "created_time": (order.date_created + config.TIMEZONE_OFFSET).strftime("%H:%M:%S"),
        "delivery_time": (order.delivery_time + config.TIMEZONE_OFFSET).strftime("%H:%M:%S"),
        "payment_type": _PAYMENT_TYPE_STRINGS[order.payment_type_id],
        "total_sum": order.total_sum if order.payment_type_id != BONUS_PAYMENT_TYPE else 0,
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
