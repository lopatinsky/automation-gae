from datetime import time
from google.appengine.api import memcache
from models.proxy.resto import RestoCompany
from models.schedule import Schedule, DaySchedule
from models.venue import SELF, DELIVERY, DeliveryType, DeliveryZone, Address, DeliverySlot
from requests import get_resto_company_info, get_resto_delivery_types

__author__ = 'dvpermyakov'


DELIVERY_TYPE_MAP = {
    'self': SELF,
    'delivery': DELIVERY
}

REVERSE_DELIVERY_TYPE_MAP = {
    SELF: 1,
    DELIVERY: 0
}


def __get_company_schedule(resto_schedule):
    schedule = Schedule()
    for resto_schedule in resto_schedule:
        resto_start_hour = int(resto_schedule['hours'].split('-')[0]) % 24
        resto_end_hour = int(resto_schedule['hours'].split('-')[1]) % 24
        for day in resto_schedule['days']:
            schedule.days.append(DaySchedule(weekday=int(day),
                                             start=time(hour=resto_start_hour),
                                             end=time(hour=resto_end_hour)))
    return schedule


def __get_delivery_types(resto_delivery_types, resto_delivery_cities, resto_min_sum):
    delivery_types = []
    delivery_zones = {}
    for resto_deliery_type in resto_delivery_types:
        delivery_type = DeliveryType()
        delivery_type.delivery_type = DELIVERY_TYPE_MAP[resto_deliery_type['name']]
        delivery_type.delivery_slots = DeliverySlot.query().fetch(keys_only=True)
        delivery_type.status = resto_deliery_type['available']
        if delivery_type.delivery_type == DELIVERY:
            for id, city in enumerate(resto_delivery_cities):
                zone = DeliveryZone(id=id+1, address=Address(city=city), min_sum=resto_min_sum)
                delivery_type.delivery_zones.append(zone.key)
                delivery_zones[zone.key] = zone
        delivery_types.append(delivery_type)
    return delivery_types, delivery_zones


def __get_company_info_dict(resto_company_info):
    return {
        'app_name': resto_company_info['app_name'],
        'description': resto_company_info['description'],
        'phone': resto_company_info['phone'],
        'site': resto_company_info['site'],
        'emails': resto_company_info['support_emails']
    }


def _get_company_info():
    resto_company = RestoCompany.get()
    resto_company_info = get_resto_company_info(resto_company)
    resto_delivery_types = get_resto_delivery_types(resto_company)
    schedule = memcache.get('schedule_%s' % resto_company.key.id())
    if not schedule:
        schedule = __get_company_schedule(resto_company_info['schedule'])
        memcache.set('schedule_%s' % resto_company.key.id(), schedule, time=3600)
    delivery_types = memcache.get('delivery_types_%s' % resto_company.key.id())
    delivery_zones = memcache.get('delivery_zones_%s' % resto_company.key.id())
    if not delivery_types or not delivery_zones:
        delivery_types, delivery_zones = __get_delivery_types(resto_delivery_types['types'],
                                                              resto_company_info['cities'],
                                                              resto_company_info['min_order_sum'])
        memcache.set('delivery_types_%s' % resto_company.key.id(), delivery_types, time=3600)
        memcache.set('delivery_zones_%s' % resto_company.key.id(), delivery_zones, time=3600)
    company_info_dict = memcache.get('company_info_%s' % resto_company.key.id())
    if not company_info_dict:
        company_info_dict = __get_company_info_dict(resto_company_info)
        memcache.set('company_info_%s' % resto_company.key.id(), company_info_dict, time=3600)
    return schedule, delivery_types, delivery_zones, company_info_dict


def get_company_schedule():
    return _get_company_info()[0]


def get_delivery_types():
    return _get_company_info()[1]


def get_delivery_zone(zone_key):
    return _get_company_info()[2][zone_key]


def get_company_info_dict():
    return _get_company_info()[3]
