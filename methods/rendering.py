import time


def timestamp(datetime_object):
    return int(time.mktime(datetime_object.timetuple()))


def opt(fn, value):
    return fn(value) if value is not None else None
