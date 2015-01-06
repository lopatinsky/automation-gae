# coding=utf-8
from collections import Counter
from datetime import datetime
from ..base import BaseHandler
from config import config
from handlers.maintenance.report.report_methods import suitable_date, PROJECT_STARTING_YEAR
from models import Order, Client, NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER, \
    CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE, BONUS_PAYMENT_TYPE, Venue


_STATUS_STRINGS = {
    NEW_ORDER: u"Новый",
    READY_ORDER: u"Выдан",
    CANCELED_BY_CLIENT_ORDER: u"Отменен клиентом",
    CANCELED_BY_BARISTA_ORDER: u"Отменен бариста"
}

_PAYMENT_TYPE_STRINGS = {
    CASH_PAYMENT_TYPE: u"Наличные",
    CARD_PAYMENT_TYPE: u"Карта",
    BONUS_PAYMENT_TYPE: u"Бонусы"
}


def _order_data(order):
    dct = {
        "order_id": order.key.id(),
        "status": _STATUS_STRINGS[order.status],
        "date": (order.date_created + config.TIMEZONE_OFFSET).strftime("%d.%m.%Y"),
        "created_time": (order.date_created + config.TIMEZONE_OFFSET).strftime("%H:%M:%S"),
        "delivery_time": (order.delivery_time + config.TIMEZONE_OFFSET).strftime("%H:%M:%S"),
        "payment_type": _PAYMENT_TYPE_STRINGS[order.payment_type_id],
        "total_sum": order.total_sum if order.payment_type_id != BONUS_PAYMENT_TYPE else 0,
        "venue": Venue.get_by_id(order.venue_id).title[22:],  # strip "Double B Coffee & Tea "
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


class OrdersReportHandler(BaseHandler):
    def get(self):
        venue_id = self.request.get_range("selected_venue")
        chosen_year = self.request.get("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        if not chosen_year:
            chosen_month = 0
        if not chosen_month:
            chosen_day = 0
        if not chosen_year:
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
            chosen_day = datetime.now().day
        else:
            chosen_year = int(chosen_year)

        start = suitable_date(chosen_day, chosen_month, chosen_year, True)
        end = suitable_date(chosen_day, chosen_month, chosen_year, False)
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
        self.render('reported_orders.html', **values)
