import datetime
from models import Order, Client


def search_orders(query, start=None, end=None):
    if not start:
        start = datetime.datetime.min
    if not end:
        end = datetime.datetime.max
    result = []
    # search by order number
    try:
        order_by_number = Order.get_by_id(int(query))
    except ValueError:
        pass
    else:
        if start < order_by_number.date_created < end:
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
        result.extend(Order.query(Order.date_created >= start, Order.date_created < end,
                                  Order.client_id == client_key.id()).fetch())
    return result
