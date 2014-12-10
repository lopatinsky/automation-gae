__author__ = 'dvpermyakov'

from .base import BaseHandler
from models import TabletQuery
from datetime import datetime, timedelta


class QueryNumber():
    def __init__(self, admin_id, token):
        self.admin_id = admin_id
        self.token = token
        self.number = 1

    def add_query(self):
        self.number += 1


class TabletRequestReportHandler(BaseHandler):

    @staticmethod
    def group_queries(chosen_time_min):
        shift_date = datetime.now() - timedelta(minutes=chosen_time_min)
        history_tablet_queries = TabletQuery.query(TabletQuery.query_time >= shift_date).fetch()
        tokens = []
        queries = {}
        for query in history_tablet_queries:
            if not query.token in tokens:
                tokens.append(query.token)
                queries[tokens.index(query.token)] = QueryNumber(query.admin_id, query.token)
            else:
                queries[tokens.index(query.token)].add_query()
        return queries.values()

    def get(self):
        chosen_time_min = self.request.get_range("selected_time_min")
        self.render('reported_tablet_queries.html', queries=self.group_queries(chosen_time_min), chosen_time=chosen_time_min)