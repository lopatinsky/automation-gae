# coding=utf-8
import datetime
from .base import BaseHandler
from .methods import format_order
from models import Order, NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER, CARD_PAYMENT_TYPE, \
    CASH_PAYMENT_TYPE, Client


def search_orders(query):
    result = []
    # search by order number
    try:
        order_by_number = Order.get_by_id(int(query))
    except ValueError:
        pass
    else:
        result.append(order_by_number)

    # search by client
    client_keys = []
    # by client tel
    client_keys.extend(Client.query(Client.tel == query).fetch(keys_only=True))
    # by client name
    terms = query.split(None, 1)
    if len(terms) == 1:
        client_keys.extend(Client.query(Client.name == query or Client.surname == query).fetch(keys_only=True))
    else:
        client_keys.extend(Client.query(Client.name == terms[0], Client.surname == terms[1]).fetch(keys_only=True))
        client_keys.extend(Client.query(Client.name == terms[1], Client.surname == terms[0]).fetch(keys_only=True))
    for client_key in client_keys:
        result.extend(Order.query(Order.client_id == client_key.id()).fetch())
    return result


class HistoryHandler(BaseHandler):
    def get(self):
        search_string = self.request.get("search")
        if search_string:
            orders = search_orders(search_string)
        else:
            today = datetime.datetime.combine(datetime.date.today(), datetime.time())
            orders = Order.query(Order.date_created >= today).order(-Order.date_created).fetch()
        orders_data = []
        total_price = 0
        total_cost_price = 0
        for order in orders:
            orders_data.append(format_order(order))
            total_price += order.total_sum
            for item in order['items']:
                total_cost_price += item['cost_price']

        status_strings = {
            NEW_ORDER: u"Новый заказ",
            READY_ORDER: u"Выдано",
            CANCELED_BY_CLIENT_ORDER: u"Отменено клиентом",
            CANCELED_BY_BARISTA_ORDER: u"Отменено баристой"
        }
        payment_type_strings = {
            CARD_PAYMENT_TYPE: u"Карта",
            CASH_PAYMENT_TYPE: u"Наличными"
        }

        self.render('history.html', orders=orders_data, status_strings=status_strings,
                    payment_type_strings=payment_type_strings)
