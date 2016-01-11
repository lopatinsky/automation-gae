# coding=utf-8
from google.appengine.ext import ndb

__author__ = 'dvpermyakov'


class ScheduleItem(ndb.Model):
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

    def get_restriction_time_str(self, what):
        return u'Заказы %s доступны c %s до %s.' % (what, self.start_str(), self.end_str())

    def get_time_break_str(self):
        return u'Перерыв c %s до %s.' % (self.start_str(), self.end_str())


class DaySchedule(ScheduleItem):
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
    DAY_SHORT_MAP = {
        1: u'Пн',
        2: u'Вт',
        3: u'Ср',
        4: u'Чт',
        5: u'Пт',
        6: u'Сб',
        7: u'Вс'
    }

    weekday = ndb.IntegerProperty(required=True, choices=DAYS)

    def compare(self, day, weekday_include=False):
        result = self.start == day.start and self.end == day.end
        if weekday_include:
            result = result and self.weekday == day.weekday
        return result

    def interval_str(self, day):
        hours_interval_str = '%s-%s' % (self.start_str(), self.end_str())
        if self.compare(day, weekday_include=True):
            return '%s: %s' % (self.DAY_SHORT_MAP[self.weekday], hours_interval_str)
        else:
            return '%s-%s: %s' % (self.DAY_SHORT_MAP[self.weekday], day.DAY_SHORT_MAP[day.weekday], hours_interval_str)

    def short_str(self):
        return u'%s, %s - %s' % (self.DAY_SHORT_MAP[self.weekday], self.start_str(), self.end_str())

    def str(self):
        return u'%s, %s - %s' % (self.DAY_MAP[self.weekday], self.start_str(), self.end_str())


class DateSchedule(ScheduleItem):
    date = ndb.DateProperty(required=True)
    closed = ndb.BooleanProperty(required=True)


class Schedule(ndb.Model):
    days = ndb.LocalStructuredProperty(DaySchedule, repeated=True)
    overrides = ndb.LocalStructuredProperty(DateSchedule, repeated=True)

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

    def get_item_for_date(self, date):
        for override in self.overrides:
            if override.date == date:
                if override.closed:
                    return None
                return override
        return self.get_day(date.isoweekday())

    def get_days_str(self):
        def add_interval(result):
            if result:
                result += ', '
            result += start_day.interval_str(current_day)
            return result

        result = ''
        if not self.days:
            return result
        start_day = self.days[0]
        current_day = None
        for day in self.days:
            if not start_day.compare(day):
                result = add_interval(result)
                start_day = day
            current_day = day
        result = add_interval(result)
        return result

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
