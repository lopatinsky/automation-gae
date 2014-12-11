import datetime
from config import config


def check(working_days, working_hours, time):
    working_days = working_days.split(',')
    working_hours = [s.split("-") for s in working_hours.split(',')]
    schedule = {int(d): [int(h) for h in working_hours[i]]
                for i in xrange(len(working_days))
                for d in working_days[i]}

    time += config.TIMEZONE_OFFSET

    def check_day(date):
        weekday = date.isoweekday()
        if weekday not in schedule:
            return False

        open_hours, close_hours = schedule[weekday]
        open_time = date + datetime.timedelta(hours=open_hours)
        close_time = date + datetime.timedelta(hours=close_hours)
        if close_time <= open_time:  # venue works past midnight
            close_time += datetime.timedelta(days=1)
        return open_time <= time <= close_time

    today = datetime.datetime.combine(time.date(), datetime.time())
    yesterday = today - datetime.timedelta(days=1)
    return check_day(today) or check_day(yesterday)
