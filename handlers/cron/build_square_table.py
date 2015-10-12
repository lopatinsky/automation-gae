from datetime import timedelta, datetime, time
import logging
from google.appengine.api import namespace_manager
from google.appengine.ext import deferred
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from methods.rendering import timestamp
from models.client import ANDROID_DEVICE, IOS_DEVICE
from models.order import Order, READY_ORDER
from models.specials import JsonStorage


def _add_week_task(namespace, start, week_number):
    namespace_manager.set_namespace(namespace)

    table = JsonStorage.get("square_table_tmp")
    week_start = start + timedelta(days=7 * week_number)
    week_end = week_start + timedelta(days=7)
    logging.info("starting week task for %s, week %s (%s - %s)", namespace, week_number, week_start, week_end)

    client_week = {}
    for i in xrange(week_number):
        client_ids = table[i][i]['all']['client_ids']
        for client_id in client_ids:
            client_week[client_id] = i
    logging.info("client_week before current: %s", client_week)

    orders = Order.query(Order.date_created >= week_start,
                         Order.date_created < week_end,
                         Order.status == READY_ORDER).fetch()
    logging.info("week order count: %s", len(orders))
    for order in orders:
        client_week.setdefault(order.client_id, week_number)

    weeks_count = len(table)
    orders_by_client_week = [[] for _ in xrange(weeks_count)]
    for order in orders:
        orders_by_client_week[client_week[order.client_id]].append(order)

    for i in xrange(weeks_count):
        table[i].append(_get_orders_info(orders_by_client_week[i], week_start, week_end))

    if week_number == weeks_count - 1:
        JsonStorage.save("square_table", table)
        JsonStorage.delete("square_table_tmp")
    else:
        JsonStorage.save("square_table_tmp", table)
        deferred.defer(_add_week_task, namespace, start, week_number + 1)


def _get_orders_info(orders, begin, end):
    def _add(dct, order):
        dct['order_number'] += 1
        dct['goods_number'] += len(order.item_details)
        dct['gift_number'] += len(order.gift_details) + len(order.order_gift_details)
        dct['order_sum'] += order.total_sum - order.wallet_payment
        if not order.client_id in dct['client_ids']:
            dct['client_ids'].append(order.client_id)

    def make_dict():
        return {
            'goods_number': 0,
            'order_number': 0,
            'order_sum': 0,
            'gift_number': 0,
            'client_ids': []
        }

    ios = make_dict()
    android = make_dict()
    all = make_dict()

    for order in orders:
        _add(all, order)
        if order.device_type == IOS_DEVICE:
            _add(ios, order)
        elif order.device_type == ANDROID_DEVICE:
            _add(android, order)

    ios['client_number'] = len(ios['client_ids'])
    android['client_number'] = len(android['client_ids'])
    all['client_number'] = len(all['client_ids'])

    return {
        "android": android,
        "ios": ios,
        "all": all,
        "begin": timestamp(begin),
        "end": timestamp(end - timedelta(minutes=1))
    }


def _build(namespace):
    namespace_manager.set_namespace(namespace)

    first_order_ever = Order.query().order(Order.date_created).get()
    if not first_order_ever:
        return
    start_date = first_order_ever.date_created.date()
    start_time = datetime.combine(start_date, time())

    weeks_count = (datetime.now() - start_time).days / 7 + 1
    table = [[] for _ in xrange(weeks_count)]
    JsonStorage.save("square_table_tmp", table)

    deferred.defer(_add_week_task, namespace, start_time, 0)


class BuildSquareTableHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            deferred.defer(_build, namespace)
