__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Order, Venue, READY_ORDER
from datetime import datetime
import calendar
import logging
from methods import PROJECT_STARTING_YEAR, suitable_date


class FinanceItem:
    def __init__(self, spent, received, day):
        self.spent = spent
        self.received = received
        self.day = day


class FinanceReportHandler(BaseHandler):
    @staticmethod
    def finance_table(chosen_year=0, chosen_month=0, venue_id=0):
        days_in_month = calendar.monthrange(chosen_year, chosen_month)[1]
        logging.info(days_in_month)
        finance_items = []
        for day_number in range(1, days_in_month + 1):
            query = Order.query(Order.status == READY_ORDER)
            query = query.filter(Order.date_created >= suitable_date(day_number, chosen_month, chosen_year, True))
            query = query.filter(Order.date_created <= suitable_date(day_number, chosen_month, chosen_year, False))
            if venue_id != 0:
                query = query.filter(Order.venue_id == venue_id)
            #spent = sum((item.get().price for item in order.items) for order in query.fetch())
            total_sum = sum(order.total_sum for order in query.fetch())
            price_sum = 0
            for order in query.fetch():
                for item in order.items:
                    price_sum += item.get().price
            finance_items.append(FinanceItem(price_sum - total_sum, total_sum, day_number))
        return finance_items

    def get(self):
        venue_id = self.request.get("selected_venue")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        if not chosen_year:
            chosen_month = 0
        logging.info('before venue ==')
        if not venue_id:
            logging.info('int venue')
            venue_id = 0
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
        else:
            venue_id = int(venue_id)
        if not chosen_month:
            self.render('reported_finance.html', start_year=PROJECT_STARTING_YEAR,
                        end_year=datetime.now().year, venues=Venue.query().fetch())
            return
        items = self.finance_table(chosen_year, chosen_month, venue_id)
        chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
        values = {
            'venues': Venue.query().fetch(),
            'days': items,
            'chosen_venue': chosen_venue,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
        }
        self.render('reported_finance.html', **values)
