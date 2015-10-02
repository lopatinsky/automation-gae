from models.order import READY_ORDER

__author__ = 'dvpermyakov'


from models import Order, Venue, MenuItem


class ReportedMenuItem:
    def __init__(self, item_id, title, price):
        self.item_id = item_id
        self.title = title
        self.price = price
        self.order_number = 1

    def add_order(self):
        self.order_number += 1


def menu_items_table(start, end, venue_id=0):
    suited_menu_items = {}
    query = Order.query(Order.status == READY_ORDER, Order.date_created >= start, Order.date_created < end)
    if venue_id != 0:
        query = query.filter(Order.venue_id == str(venue_id))
    for order in query.fetch():
        for item_detail in order.item_details:
            item_id = item_detail.item.id()
            if item_id in suited_menu_items:
                suited_menu_items[item_id].add_order()
            else:
                item = MenuItem.get_by_id(item_id)
                suited_menu_items[item_id] = ReportedMenuItem(item_id, item.title, item.price / 100.0)
    return suited_menu_items, \
        sum(item.order_number for item in suited_menu_items.values()),\
        sum(item.order_number * item.price for item in suited_menu_items.values())


def get(venue_id, start, end):
    if not venue_id:
        venue_id = 0
    else:
        venue_id = int(venue_id)

    menu_items, menu_item_total_number, menu_item_total_sum = menu_items_table(start, end, venue_id)
    chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
    values = {
        'venues': Venue.query().fetch(),
        'menu_items': menu_items.values(),
        'menu_item_number': menu_item_total_number,
        'menu_item_expenditure': menu_item_total_sum,
        'chosen_venue': chosen_venue,
        'start': start,
        'end': end,
    }
    return values
