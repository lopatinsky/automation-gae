__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Order, Client
from datetime import datetime, timedelta

WEEK = timedelta(days=7)


class WeekInfo:
    def __init__(self, goods_number, order_number, order_sum, gift_number, begin, end):
        self.goods_number = goods_number
        self.order_number = order_number
        self.order_sum = order_sum
        self.gift_number = gift_number
        self.begin = begin
        self.end = end


class SquareTableHandler(BaseHandler):

    def get_orders_info(self, orders):
        goods_number = 0
        order_number = len(orders)
        order_sum = 0
        gift_number = 0
        for order in orders:
            goods_number += len(order.items)
            order_sum += order.total_sum

        return goods_number, order_number, order_sum, gift_number

    def get(self):
        chosen_type = self.request.get("selected_type", 0)

        orders = Order.query().fetch()
        clients = Client.query().fetch()

        for client in clients:
            client.first_order_time = None
        clients_map = {c.key.id(): c for c in clients}

        for order in orders:
            client = clients_map[order.client_id]
            if not client.first_order_time or client.first_order_time > order.date_created:
                client.first_order_time = order.date_created

        clients = [c for c in clients if c.first_order_time is not None]
        clients = sorted(clients, key=lambda client: client.first_order_time)
        start_time = clients[0].first_order_time

        def _week_number(dt):
            return (dt - start_time).days / 7

        def _week_start(number):
            return start_time + timedelta(days=7 * number)

        weeks_count = _week_number(datetime.now()) + 1

        orders_square = []
        for i in xrange(weeks_count):
            orders_row = []
            for j in xrange(weeks_count):
                orders_row.append([])
            orders_square.append(orders_row)

        client_week = {}
        for client in clients:
            client_week[client.key.id()] = _week_number(client.first_order_time)

        for order in orders:
            row = client_week[order.client_id]
            column = _week_number(order.date_created)
            orders_square[row][column].append(order)

        square = [
            [
                WeekInfo(*self.get_orders_info(cell), begin=_week_start(i), end=_week_start(i+1))
                for i, cell in enumerate(row)
            ]
            for row in orders_square
        ]

        self.render('reported_square_table.html', square=square, chosen_type=chosen_type)
