__author__ = 'dvpermyakov'

from .base import BaseHandler
from models import TabletRequest, Admin
from datetime import datetime, timedelta
from report import PROJECT_STARTING_YEAR
import json


class AdminRequestNumber():
    def __init__(self, admin_id, token, number_parts):
        self.admin_id = admin_id
        self.login = Admin.get_by_id(admin_id).email
        self.token = token
        self.number_parts = number_parts
        self.number = [0] * number_parts

    def add_request(self, part):
        self.number[part] += 1


class TabletRequestReportHandler(BaseHandler):

    @staticmethod
    def group_requests(date, interval):
        number_parts = 24 * 60 // interval
        shift_date_min = datetime(date.year, date.month, date.day)
        shift_date_max = shift_date_min + timedelta(days=1)
        history_tablet_requests = TabletRequest.query(
            TabletRequest.request_time >= shift_date_min,
            TabletRequest.request_time <= shift_date_max).fetch()
        requests = {}
        for request in history_tablet_requests:
            if not request.token in requests:
                requests[request.token] = AdminRequestNumber(request.admin_id, request.token, number_parts)
            requests[request.token].add_request((request.request_time.hour * 60 + request.request_time.minute) // interval)

        return requests.values()

    @staticmethod
    def get_interval_numbers_json(admins):
        numbers = []
        for i, admin in enumerate(admins):
            points = []
            index = 0
            for number in admin.number:
                points.append([index, number])
                index += 1
            numbers.append({'label': admin.login, 'data': points, 'color': i})
        return numbers

    def get(self):
        chosen_interval = self.request.get_range("selected_interval")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")

        try:
            date = datetime(chosen_year, chosen_month, chosen_day)
        except ValueError:
            self.render('reported_tablet_requests_graph.html', start_year=PROJECT_STARTING_YEAR, end_year=datetime.now().year)
            return

        admins = self.group_requests(date, chosen_interval)
        numbers = self.get_interval_numbers_json(admins)

        values = {
            'numbers': json.dumps(numbers),
            'admins': admins,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day,
            'chosen_interval': chosen_interval,
        }

        self.render('reported_tablet_requests_graph.html', **values)