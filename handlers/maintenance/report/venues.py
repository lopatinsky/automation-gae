__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Order, Venue, READY_ORDER, BONUS_PAYMENT_TYPE
from datetime import datetime, timedelta
from report_methods import PROJECT_STARTING_YEAR, suitable_date


class ReportedVenue:
    def __init__(self, venue_id, name, order_sum, payment):
        self.client_id = venue_id
        self.name = name
        self.amount_orders = 1
        self.total_sum = order_sum
        self.payment = payment
        self.average_order_cost = order_sum

    def add_order(self, order_sum, payment):
        self.amount_orders += 1
        self.total_sum += order_sum
        self.payment += payment
        self.average_order_cost = self.total_sum / self.amount_orders


class VenuesReportHandler(BaseHandler):
    @staticmethod
    def venues_table_by_range(start, end):
        venues = {}
        query = Order.query(Order.status == READY_ORDER, Order.date_created >= start, Order.date_created <= end)
        for order in query.fetch():
            venue_id = order.venue_id
            total_sum = sum(item.get().price for item in order.items)
            payment = order.total_sum if order.payment_type_id != BONUS_PAYMENT_TYPE else 0
            if venue_id in venues:
                venues[venue_id].add_order(total_sum, payment)
            else:
                venue = Venue.get_by_id(venue_id)
                venues[venue_id] = ReportedVenue(venue_id, venue.title, total_sum, payment)
        return venues

    @staticmethod
    def venues_table(chosen_year=0, chosen_month=0, chosen_day=0):
        start = suitable_date(chosen_day, chosen_month, chosen_year, True)
        end = suitable_date(chosen_day, chosen_month, chosen_year, False)
        return VenuesReportHandler.venues_table_by_range(start, end)

    def get(self):
        # selected_*param == 0 if choose all *param
        chosen_year = self.request.get("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        if not chosen_year:
            chosen_month = 0
        if not chosen_month:
            chosen_day = 0
        if not chosen_year:
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
            chosen_day = datetime.now().day
        else:
            chosen_year = int(chosen_year)
        venues = self.venues_table(chosen_year, chosen_month, chosen_day)
        values = {
            'venues': venues.values(),
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day
        }
        self.render('reported_venues.html', **values)


class VenuesReportWithDatesHandler(VenuesReportHandler):
    @staticmethod
    def venues_table_with_dates(chosen_year, chosen_month):
        range_start = suitable_date(0, chosen_month, chosen_year, True)
        range_end = suitable_date(0, chosen_month, chosen_year, False)
        date = range_start
        result = []
        while date < range_end:
            next_date = date + timedelta(days=1)
            table = VenuesReportWithDatesHandler.venues_table_by_range(date, next_date).values()
            result.append((date, table))
            date = next_date
        return result

    def get(self):
        chosen_year = self.request.get("selected_year")
        chosen_month = self.request.get_range("selected_month")
        if not chosen_year:
            chosen_month = 0
        if not chosen_year:
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
        else:
            chosen_year = int(chosen_year)
        venues = self.venues_table_with_dates(chosen_year, chosen_month)
        values = {
            'report_data': venues,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month
        }
        self.render('reported_venues_with_dates.html', **values)
