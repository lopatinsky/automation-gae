__author__ = 'dvpermyakov'

from .base import BaseHandler
from models import TabletQuery
from datetime import datetime, timedelta
from report import suitable_date, PROJECT_STARTING_YEAR


class QueryNumber():
    def __init__(self, admin_id, token, number_parts):
        self.admin_id = admin_id
        self.token = token
        self.number_parts = number_parts
        self.number = [0] * number_parts

    def add_query(self, part):
        self.number[part] += 1


class TabletRequestReportHandler(BaseHandler):

    @staticmethod
    def valid_date(year, month, day):
        if year == 0:
            return False
        if month == 0:
            return False
        if day == 0:
            return False
        return True

    @staticmethod
    def group_queries(date, interval):
        number_parts = 24 * 60 // interval
        shift_date_min = suitable_date(date.day, date.month, date.year, True)
        shift_date_max = suitable_date(date.day, date.month, date.year, False)
        history_tablet_queries = TabletQuery.query(
            TabletQuery.query_time >= shift_date_min,
            TabletQuery.query_time <= shift_date_max).fetch()
        tokens = []
        queries = {}
        for query in history_tablet_queries:
            print "In for query in history"
            if not query.token in tokens:
                tokens.append(query.token)
                queries[tokens.index(query.token)] = QueryNumber(query.admin_id, query.token, number_parts)
            queries[tokens.index(query.token)].add_query((query.query_time.hour * 60 + query.query_time.minute) // interval)

        return queries.values()

    def get(self):
        chosen_interval = self.request.get_range("selected_interval")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")

        if not self.valid_date(chosen_year, chosen_month, chosen_day):
            self.render('reported_tablet_queries_graph.html', start_year=PROJECT_STARTING_YEAR, end_year=datetime.now().year)
            return

        date = datetime.now().replace(year=chosen_year, month=chosen_month, day=chosen_day)
        values = {
            'admins': self.group_queries(date, chosen_interval),
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day,
            'chosen_interval': chosen_interval,
        }

        self.render('reported_tablet_queries_graph.html', **values)