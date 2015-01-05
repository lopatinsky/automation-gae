__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Order, Venue, MenuItem, READY_ORDER
from datetime import datetime
from methods import PROJECT_STARTING_YEAR, suitable_date

class ReportedMenuItem:
    def __init__(self, item_id, title, price):
        self.item_id = item_id
        self.title = title
        self.price = price
        self.order_number = 1

    def add_order(self):
        self.order_number += 1


class MenuItemsReportHandler(BaseHandler):
    @staticmethod
    def menu_items_table(chosen_year=0, chosen_month=0, chosen_day=0, venue_id=0):
        suited_menu_items = {}
        query = Order.query(Order.status == READY_ORDER)
        query = query.filter(Order.date_created >= suitable_date(chosen_day, chosen_month, chosen_year, True))
        query = query.filter(Order.date_created <= suitable_date(chosen_day, chosen_month, chosen_year, False))
        if venue_id != 0:
            query = query.filter(Order.venue_id == venue_id)
        for order in query.fetch():
            for item_in_order in order.items:
                item_id = item_in_order.id()
                if item_id in suited_menu_items:
                    suited_menu_items[item_id].add_order()
                else:
                    item = MenuItem.get_by_id(item_id)
                    suited_menu_items[item_id] = ReportedMenuItem(item_id, item.title, item.price)
        return suited_menu_items, \
            sum(item.order_number for item in suited_menu_items.values()),\
            sum(item.order_number * item.price for item in suited_menu_items.values())

    def get(self):
        # selected_*param == 0 if choose all *param
        venue_id = self.request.get("selected_venue")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        if not chosen_year:
            chosen_month = 0
        if not chosen_month:
            chosen_day = 0
        if not venue_id:
            venue_id = 0
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
            chosen_day = datetime.now().day
        else:
            venue_id = int(venue_id)
        menu_items, menu_item_total_number, menu_item_total_sum = self.menu_items_table(chosen_year,
                                                                                        chosen_month,
                                                                                        chosen_day,
                                                                                        venue_id)
        chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
        values = {
            'venues': Venue.query().fetch(),
            'menu_items': menu_items.values(),
            'menu_item_number': menu_item_total_number,
            'menu_item_expenditure': menu_item_total_sum,
            'chosen_venue': chosen_venue,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day
        }
        self.render('reported_menu_items.html', **values)