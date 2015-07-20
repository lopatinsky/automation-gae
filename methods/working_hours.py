# coding=utf-8
from datetime import datetime, timedelta


def check(schedule, time):
    def check_day(date):
        weekday = date.isoweekday()
        day = schedule.get_day(weekday)
        if not day:
            return False
        open_time = datetime.combine(date, day.start)
        close_time = datetime.combine(date, day.end)
        if close_time <= open_time:  # venue works past midnight
            close_time += timedelta(days=1)
        return open_time <= time <= close_time

    today = time.date()
    yesterday = (time - timedelta(days=1)).date()
    return check_day(today) or check_day(yesterday)


def check_with_errors(schedule, time):
    valid = check(schedule, time)
    if valid:
        return True, None
    day = schedule.get_day(time.isoweekday())
    if not day:
        return False, u'Заказы в этот день недели недоступны.'
    else:
        return False, day.get_valid_time_str()