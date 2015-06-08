from collections import Counter
from models import Client
from models.order import CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER
from models.payment_types import CASH_PAYMENT_TYPE


def format_phone(phone):
    phone = "".join(c for c in phone if '0' <= c <= '9')
    if len(phone) != 11:
        return phone
    return "+%s (%s) %s-%s-%s" % (phone[0], phone[1:4], phone[4:7], phone[7:9], phone[9:])


def format_order(order):
    client = Client.get_by_id(order.client_id)
    order_data = {
        'date_created': order.date_created.strftime("%Y-%m-%d %H:%M:%S"),
        'comment': order.comment,
        'payment_type_id': order.payment_type_id,
        'payment_type': 'cash' if order.payment_type_id == CASH_PAYMENT_TYPE else 'card',
        'order_id': order.key.id(),
        'client': {
            'pan': order.pan,
            'name': client.name,
            'surname': client.surname,
            'tel': format_phone(client.tel),
        },
        'delivery_time': order.delivery_time.strftime("%H:%M"),
        'delivery_datetime': order.delivery_time.strftime("%b %d %H:%M"),
        'items': [],
        'total_sum': order.total_sum,
        'cost_price': 0,
        'status': order.status,
        'canceled': order.status in (CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER)
    }
    item_keys = Counter(order.items).items()
    for key, count in item_keys:
        item = key.get()
        order_data['items'].append({
            'title': item.title,
            'price': item.price,
            'cost_price': item.cost_price * count,
            'quantity': count
        })
        order_data['cost_price'] += item.cost_price * count
    return order_data
