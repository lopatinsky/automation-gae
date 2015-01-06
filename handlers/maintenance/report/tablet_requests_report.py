__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import TabletRequest, Admin, AdminStatus
from datetime import datetime, timedelta
from report_methods import PROJECT_STARTING_YEAR
from methods import location
import json
import time
import logging


class AdminRequestNumber():
    def __init__(self, admin_id, token, number_parts):
        self.admin_id = admin_id
        self.login = Admin.get_by_id(admin_id).email
        self.token = token
        self.number_parts = number_parts
        self.number = [0] * number_parts

    def add_request(self, part):
        self.number[part] += 1


class TabletRequestGraphHandler(BaseHandler):

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
        values = {
            'numbers': json.dumps(numbers),
            'admins': admins,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day,
            'chosen_interval': chosen_interval
        }
        self.render('reported_tablet_requests_graph.html', **values)


RED_CODE = '#DF0101'
GREEN_CODE = '#04B404'
GRAY_CODE = '#6E6E6E'

AVAIL_PING_PER_10 = 4
AVAIL_BATTERY_LEVEL = 10
AVAIL_SOUND_LEVEL = 10


class TabletInfoHandler(BaseHandler):

    def check(self, admin_info):
        if not admin_info.app_version:
            return False
        if admin_info.error_sum or \
                admin_info.ping_number < AVAIL_PING_PER_10 or \
                admin_info.is_turned_on or \
                (not admin_info.is_in_charging and admin_info.battery_level < AVAIL_BATTERY_LEVEL) or \
                admin_info.sound_level_system < AVAIL_SOUND_LEVEL:
            return False
        else:
            return True

    def get(self):
        admins_info = []
        statuses = AdminStatus.query().fetch()
        for status in statuses:
            if status.admin.venue is None:
                continue
            requests = TabletRequest.query(TabletRequest.token == status.token,
                                           TabletRequest.request_time > datetime.now() - timedelta(minutes=10)).\
                order(-TabletRequest.request_time).fetch()
            if not requests:
                admin_info = TabletRequest.query(TabletRequest.token == status.token).\
                    order(-TabletRequest.request_time).get()
                if not admin_info:
                    admin_info = TabletRequest()
                    admin = status.admin
                    admin_info.admin_id = admin.key.id()
                    admin_info.name = admin.email
                    admin_info.token = status.token
                    admin_info.ping_number = 0
                    continue
                admin_info.color = RED_CODE
            else:
                admin_info = requests[0]
                admin_info.color = None
            admin_info.name = Admin.get_by_id(admin_info.admin_id).email
            admin_info.ping_number = len(requests)
            admin_info.distance = location.distance(admin_info.location, status.location)
            admin_info.error_sum = sum(request.error_number for request in requests) if admin_info.app_version else 0
            if not status.admin.venue.get().active:
                admin_info.color = GRAY_CODE
            elif not self.check(admin_info):
                admin_info.color = RED_CODE
            elif not admin_info.color:
                admin_info.color = GREEN_CODE
            admins_info.append(admin_info)
        self.render('reported_tablet_requests_info.html', admins_info=admins_info)