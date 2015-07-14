# coding=utf-8
from google.appengine.ext import ndb

__author__ = 'dvpermyakov'


class DaySchedule(ndb.Model):
    DAYS = (1, 2, 3, 4, 5, 6, 7)
    DAY_MAP = {
        1: u'Понедельник',
        2: u'Вторник',
        3: u'Среда',
        4: u'Четверг',
        5: u'Пятница',
        6: u'Суббота',
        7: u'Воскресенье'
    }

    weekday = ndb.IntegerProperty(required=True, choices=DAYS)
    start = ndb.TimeProperty(required=True)
    end = ndb.TimeProperty(required=True)

    def start_str(self):
        from methods.rendering import STR_TIME_FORMAT
        return self.start.strftime(STR_TIME_FORMAT)

    def end_str(self):
        from methods.rendering import STR_TIME_FORMAT
        return self.end.strftime(STR_TIME_FORMAT)

    def get_valid_time_str(self):
        return u'Заказы в этот день доступны c %s до %s.' % (self.start_str(), self.end_str())

    def str(self):
        return u'%s, %s - %s' % (self.DAY_MAP[self.weekday], self.start_str(), self.end_str())


class Schedule(ndb.Model):
    days = ndb.LocalStructuredProperty(DaySchedule, repeated=True)

    def get_days(self, start, end):
        days = []
        for day in self.days:
            if day.start == start and day.end == end:
                days.append(day)
        return days

    def get_day(self, weekday):
        for day in self.days:
            if day.weekday == weekday:
                return day

    def dict(self):
        days_in_result = []
        result = []
        for day in self.days:
            if day not in days_in_result:
                days = self.get_days(day.start, day.end)
                days_in_result.extend(days)
                result.append({
                    'days': [day.weekday for day in days],
                    'hours': '%s-%s' % (day.start.hour, day.end.hour),
                    'minutes': '%s-%s' % (day.start.minute, day.end.minute)
                })
        return result