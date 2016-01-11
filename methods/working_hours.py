# coding=utf-8
from datetime import datetime, timedelta


def _check_day(date, day, time):
    open_time = datetime.combine(date, day.start)
    close_time = datetime.combine(date, day.end)
    if close_time <= open_time:  # venue works past midnight
        close_time += timedelta(days=1)
    return open_time <= time <= close_time


def check(schedule, time):
    def check_day(date):
        day = schedule.get_item_for_date(date)
        if not day:
            return False
        return _check_day(date, day, time)

    today = time.date()
    yesterday = (time - timedelta(days=1)).date()
    return check_day(today) or check_day(yesterday)


def check_with_errors(schedule, time):
    valid = check(schedule, time)
    if valid:
        return True, None
    day = schedule.get_item_for_date(time.date())
    if not day:
        return False, u'Заказы в этот день недоступны.'
    else:
        return False, day.get_valid_time_str()


def check_today_error(schedule_day, time):
    today = time.date()
    valid = _check_day(today, schedule_day, time)
    if not valid:
        return False, schedule_day.get_restriction_time_str(u'на сегодня')
    else:
        return True, None


def check_in_with_errors(schedule, time):
    valid = check(schedule, time)
    if valid:
        day = schedule.get_day(time.isoweekday())
        return False, day.get_time_break_str()
    else:
        return True, None


def check_restriction(schedule, time, what):
    if not schedule:
        return True, None
    day = schedule.get_day(time.isoweekday())
    if not day:
        return True, None
    if day.start == day.end:
        return False, u'Заказы %s в этот день недоступны' % what
    valid = check(schedule, time)
    if not valid:
        return False, day.get_restriction_time_str(what)
    else:
        return True, None
