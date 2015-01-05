__author__ = 'dvpermyakov'

from .base import BaseHandler
from models import TabletRequest, Admin
from datetime import datetime, timedelta
from report import PROJECT_STARTING_YEAR
import json
import time
import operator
import logging

MAX_NUMBER_LAST_PING = 10


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
    def group_requests(init_requests, interval):
        number_parts = 24 * 60 // interval
        requests = {}
        for request in init_requests:
            if not request.token in requests:
                requests[request.token] = AdminRequestNumber(request.admin_id, request.token, number_parts)
            requests[request.token].add_request(
                (request.request_time.hour * 60 + request.request_time.minute) // interval)
        return requests.values()

    @staticmethod
    def get_interval_numbers_json(date, admins):
        numbers = []
        for i, admin in enumerate(admins):
            points = []
            index = 0
            for number in admin.number:
                cur_time = (24 * 60 // admin.number_parts) * index
                hour = cur_time // 60
                minute = cur_time % 60
                points.append([time.mktime(datetime(date.year, date.month, date.day, hour, minute).timetuple()) * 1000,
                               number])
                index += 1
            numbers.append({'label': admin.login, 'data': points, 'color': i})
        return numbers

    def get(self):
        chosen_interval = self.request.get_range("selected_interval")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get("selected_day")
        if not chosen_day:
            chosen_interval = 10
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
            chosen_day = datetime.now().day
        else:
            chosen_day = int(chosen_day)
        try:
            date = datetime(chosen_year, chosen_month, chosen_day)
        except ValueError:
            self.render('reported_tablet_requests_graph.html',
                        start_year=PROJECT_STARTING_YEAR,
                        end_year=datetime.now().year)
            return
        requests = TabletRequest.query(TabletRequest.request_time >= date,
                                       TabletRequest.request_time <= date + timedelta(days=1))\
            .order(TabletRequest.request_time).fetch()
        admins = self.group_requests(requests, chosen_interval)
        numbers = self.get_interval_numbers_json(date, admins)
        admins_info = {}
        admins_indexes = {}
        for request in requests:
            request.name = Admin.get_by_id(request.admin_id).email
            if admins_indexes.get(request.token) is None:
                admins_indexes[request.token] = 0
            else:
                admins_indexes[request.token] += 1
                admins_indexes[request.token] %= MAX_NUMBER_LAST_PING
            admins_info[request.token + str(admins_indexes[request.token])] = request
        logging.info(admins_info.keys())
        admins_info = admins_info.values()
        admins_info = sorted(admins_info, key=lambda x: (x.token, x.request_time))
        values = {
            'numbers': json.dumps(numbers),
            'admins': admins,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day,
            'chosen_interval': chosen_interval,
            'admins_info': admins_info,
        }
        self.render('reported_tablet_requests_graph.html', **values)