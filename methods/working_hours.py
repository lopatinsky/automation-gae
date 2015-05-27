# coding=utf-8
import datetime


def _date_str_to_date(date_str):
    year, month, date = int(date_str[:4]), int(date_str[4:6]), int(date_str[6:])
    return datetime.datetime(year, month, date)


def _get_schedule(working_days, working_hours):
    working_days = working_days.split(',')
    working_hours = [s.split("-") for s in working_hours.split(',')]
    schedule = {
        int(d): [int(h) for h in working_hours[i]] for i in xrange(len(working_days)) for d in working_days[i]
    }
    return schedule


def _parse_overrides(overrides):
    overrides_dict = {}
    if overrides:
        for override in overrides.split(';'):
            dates_str, hours_str = override.split(':')
            hours = [int(h) for h in hours_str.split('-')] if hours_str else None

            if '-' not in dates_str:
                dates_str += '-' + dates_str
            date_start_str, date_end_str = dates_str.split('-')
            date_start, date_end = _date_str_to_date(date_start_str), _date_str_to_date(date_end_str)

            while date_start <= date_end:
                overrides_dict[date_start] = hours
                date_start += datetime.timedelta(days=1)
    return overrides_dict


def check(working_days, working_hours, time, overrides=None):
    schedule = _get_schedule(working_days, working_hours)

    overrides_dict = _parse_overrides(overrides)

    def check_day(date):
        weekday = date.isoweekday()
        date_schedule = schedule.get(weekday)
        if date in overrides_dict:
            date_schedule = overrides_dict[date]
        if not date_schedule:
            return False

        open_hours, close_hours = date_schedule
        open_time = date + datetime.timedelta(hours=open_hours)
        close_time = date + datetime.timedelta(hours=close_hours)
        if close_time <= open_time:  # venue works past midnight
            close_time += datetime.timedelta(days=1)
        return open_time <= time <= close_time

    today = datetime.datetime.combine(time.date(), datetime.time())
    yesterday = today - datetime.timedelta(days=1)
    return check_day(today) or check_day(yesterday)


def get_valid_time_str(working_days, working_hours, time):
    schedule = _get_schedule(working_days, working_hours)
    weekday = time.isoweekday()
    start, end = schedule.get(weekday)
    if start < 10:
        start = '0%s' % start
    if end < 10:
        end = '0%s' % end
    return u'Заказы в этот день доступны c %s:00 до %s:00.' % (start, end)


def is_valid_weekday(working_days, working_hours, time):
    schedule = _get_schedule(working_days, working_hours)
    weekday = time.isoweekday()
    if weekday not in schedule:
        return False, u'Заказы в этот день недели недоступны. Выберите другой день.'
    else:
        return True, None