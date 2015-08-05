from datetime import time
from config import Config
from models.schedule import Schedule, DaySchedule
from requests import get_resto_company_info

__author__ = 'dvpermyakov'


def _get_company_info():
    config = Config.get()
    resto_company = config.RESTO_COMPANY.get()
    resto_company_info = get_resto_company_info(resto_company)
    schedule = Schedule()
    for resto_schedule in resto_company_info['schedule']:
        resto_start_hour = int(resto_schedule['hours'].split('-')[0])
        resto_end_hour = int(resto_schedule['hours'].split('-')[1])
        for day in resto_schedule['days']:
            schedule.days.append(DaySchedule(weekday=int(day),
                                             start=time(hour=resto_start_hour),
                                             end=time(hour=resto_end_hour)))
    return schedule


def get_company_schedule():
    company_info = _get_company_info()
    return company_info