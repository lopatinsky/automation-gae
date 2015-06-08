from datetime import timedelta, datetime
from webapp2 import RequestHandler
from methods.rendering import timestamp
from models import Order, Client, JsonStorage
from models.order import READY_ORDER


class BuildSquareTableHandler(RequestHandler):
    def get_orders_info(self, orders, begin, end):
        goods_number = 0
        order_number = len(orders)
        order_sum = 0
        gift_number = 0
        client_ids = []
        for order in orders:
            goods_number += len(order.items)
            order_sum += order.total_sum
            if order.payment_type_id == 666:
                gift_number += 1
            if not order.client_id in client_ids:
                client_ids.append(order.client_id)

        return {
            "goods_number": goods_number,
            "order_number": order_number,
            "order_sum": order_sum,
            "gift_number": gift_number,
            "client_number": len(client_ids),
            "begin": timestamp(begin),
            "end": timestamp(end - timedelta(minutes=1))
        }

    def get(self):
        orders = Order.query(Order.status == READY_ORDER).fetch()
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
        start_time = start_time.replace(hour=0, minute=0)

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
                self.get_orders_info(cell, begin=_week_start(i), end=_week_start(i+1))
                for i, cell in enumerate(row)
            ]
            for row in orders_square
        ]
        JsonStorage.save("square_table", square)
