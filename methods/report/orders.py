# coding=utf-8
from datetime import timedelta
from models.config.config import config
from models.order import STATUS_MAP, READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER
from models.payment_types import PAYMENT_TYPE_MAP, CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE, \
    CARD_COURIER_PAYMENT_TYPE
from models.venue import DELIVERY_MAP
from models import Order, Client, Venue


def _get_venue(venue_id, cache):
    result = cache.get(venue_id)
    if not result:
        result = Venue.get(venue_id)
        cache[venue_id] = result
    return result


def _order_data(order, lite, venue_cache):
    venue = _get_venue(order.venue_id, venue_cache)
    dct = {
        "order_id": order.key.id(),
        "comment": order.comment if order.comment else '',
        "return_comment": order.return_comment if order.return_comment else '',
        "status": STATUS_MAP[order.status],
        "date": (order.date_created + timedelta(hours=venue.timezone_offset)).strftime("%d.%m.%Y"),
        "created_time": (order.date_created + timedelta(hours=venue.timezone_offset)).strftime("%H:%M:%S"),
        "delivery_time": (order.delivery_time + timedelta(hours=venue.timezone_offset)).strftime("%H:%M:%S"),
        "payment_type": PAYMENT_TYPE_MAP[order.payment_type_id],
        "menu_sum": sum(d.price / 100.0 for d in order.item_details),
        "sum_after_promos": order.total_sum - order.delivery_sum,
        "sum_after_delivery": order.total_sum,
        "sum_after_wallet": order.total_sum - order.wallet_payment,
        "venue_revenue": sum(d.revenue for d in order.item_details),
        "venue": venue.title,
        "delivery_type": order.delivery_type
    }
    if lite:
        dct["client"] = {"id": order.client_id}
    else:
        dct['items'] = order.grouped_item_dict(order.item_details)
        client = Client.get(order.client_id)
        dct["client"] = {
            "id": client.key.id(),
            "name": client.name,
            "surname": client.surname,
            "phone": client.tel
        }
    return dct


def _total(orders, status, payment_type):
    count = 0
    menu_sum = 0.0
    sum_after_promos = 0.0
    sum_after_delivery = 0.0
    sum_after_wallet = 0.0

    for order in orders:
        if (status is not None and order.status != status) or \
                (payment_type is not None and order.payment_type_id != payment_type):
            continue
        count += 1
        menu_sum += sum(d.price / 100.0 for d in order.item_details)
        sum_after_promos += order.total_sum - order.delivery_sum
        sum_after_delivery += order.total_sum
        sum_after_wallet += order.total_sum - order.wallet_payment
    return {
        "orders_number": count,
        "status": STATUS_MAP[status] if status is not None else u'Все статусы',
        "payment_type": PAYMENT_TYPE_MAP[payment_type] if payment_type is not None else u'Все способы оплаты',
        "menu_sum": menu_sum,
        "sum_after_promos": sum_after_promos,
        "sum_after_delivery": sum_after_delivery,
        "sum_after_wallet": sum_after_wallet,
    }


def get(venue_id, start, end, venue_ids=(), lite=False):
    if venue_id and venue_id != '0':
        venue_ids = venue_id,

    query = Order.query(Order.date_created >= start, Order.date_created <= end)
    if venue_ids:
        query = query.filter(Order.venue_id.IN(venue_ids))
    orders = query.fetch()
    venue_cache = {}
    order_dicts = [_order_data(order, lite, venue_cache) for order in orders]

    totals = [
        _total(orders, READY_ORDER, CASH_PAYMENT_TYPE),
        _total(orders, READY_ORDER, CARD_PAYMENT_TYPE),
        _total(orders, READY_ORDER, PAYPAL_PAYMENT_TYPE) if config.PAYPAL_CLIENT_ID else None,
        _total(orders, READY_ORDER, CARD_COURIER_PAYMENT_TYPE),
        _total(orders, CANCELED_BY_CLIENT_ORDER, None),
        _total(orders, CANCELED_BY_BARISTA_ORDER, None)
    ]
    totals = filter(None, totals)

    values = {
        'lite': lite,
        'venues': Venue.query().fetch(),
        'orders': order_dicts,
        'chosen_venue': venue_id,
        'start': start,
        'end': end,
        'totals': totals,
        'DELIVERY_TYPE_MAP': DELIVERY_MAP
    }
    return values
