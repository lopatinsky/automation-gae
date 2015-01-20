__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Order, Client
from datetime import datetime, timedelta

WEEK = timedelta(days=7)


class WeekInfo:
    def __init__(self, goods_number, order_number, order_sum, gift_number, begin, end, cell_id):
        self.goods_number = goods_number
        self.order_number = order_number
        self.order_sum = order_sum
        self.gift_number = gift_number
        self.begin = begin
        self.end = end
        self.cell_id = cell_id


class SquareTableHandler(BaseHandler):

    def get_clients_at_time(self, clients, begin, end):
        result = []
        for client in clients:
            if begin <= client.first_order_time <= end:
                result.append(client)
        return result

    def get_client_orders_at_time(self, client, begin, end):
        return Order.query(Order.client_id == client.key.id(), Order.date_created >= begin, Order.date_created <= end).\
            fetch()

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

        #orders = Order.query().fetch()
        clients = Client.query().fetch()
        for client in clients[:]:
            first_order = Order.query(Order.client_id == client.key.id()).order(Order.date_created).get()
            if first_order:
                client.first_order_time = first_order.date_created
            else:
                clients.remove(client)
        #sorted(clients, key=lambda client: client.first_order_time)
        start_time = clients[0].first_order_time
        current_time = start_time
        square = []
        index_id = 0
        while current_time <= datetime.now():
            week_clients = self.get_clients_at_time(clients, current_time, current_time + WEEK)
            row_time = start_time
            row = []
            while row_time <= datetime.now():
                index_id += 1
                week_info_params = 0, 0, 0, 0
                for client in week_clients:
                    week_orders = self.get_client_orders_at_time(client, row_time, row_time + WEEK)
                    week_info_params = tuple(sum(t) for t in zip(self.get_orders_info(week_orders), week_info_params))
                goods_number, order_number, order_sum, gift_number = week_info_params
                row.append(WeekInfo(goods_number, order_number, order_sum, gift_number, row_time, row_time + WEEK,
                                    index_id))
                row_time += WEEK
            square.append(row)
            current_time += WEEK
        self.render('reported_square_table.html', square=square)