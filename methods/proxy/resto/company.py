from datetime import time
from google.appengine.api import memcache
from models.proxy.resto import RestoCompany
from models.schedule import Schedule, DaySchedule
from models.venue import SELF, DELIVERY, DeliveryType, DeliveryZone, Address, DeliverySlot, IN_CAFE
from requests import get_resto_company_info, get_resto_delivery_types

__author__ = 'dvpermyakov'


DELIVERY_TYPE_MAP = {
    1: SELF,
    2: IN_CAFE,
    0: DELIVERY,
}

REVERSE_DELIVERY_TYPE_MAP = {
    SELF: 1,
    IN_CAFE: 2,
    DELIVERY: 0,
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
    for resto_delivery_type in resto_delivery_types:
        delivery_type = DeliveryType()
        delivery_type.delivery_type = DELIVERY_TYPE_MAP[resto_delivery_type['type_id']]
        if resto_delivery_type['allow_slots']:
            delivery_type.delivery_slots = DeliverySlot.query().fetch(keys_only=True)
            delivery_type.dual_mode = resto_delivery_type['allow_dual_mode']
        else:
            delivery_type.delivery_slots = []
            delivery_type.dual_mode = False
        delivery_type.min_time = resto_delivery_type['min_time']
        delivery_type.status = resto_delivery_type['available']
        if delivery_type.delivery_type == DELIVERY:
            delivery_type.min_time = 3600
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
    schedule = __get_company_schedule(resto_company_info['schedule'])
    delivery_types, delivery_zones = __get_delivery_types(resto_delivery_types['types'],
                                                          resto_company_info['cities'],
                                                          resto_company_info['min_order_sum'])
    company_info_dict = __get_company_info_dict(resto_company_info)
    return schedule, delivery_types, delivery_zones, company_info_dict


def get_company_schedule():
    resto_company = RestoCompany.get()
    schedule = memcache.get('schedule_%s' % resto_company.key.id())
    if not schedule:
        schedule = _get_company_info()[0]
        memcache.set('schedule_%s' % resto_company.key.id(), schedule, time=3600)
    return schedule


def get_delivery_types():
    resto_company = RestoCompany.get()
    delivery_types = memcache.get('delivery_type_%s' % resto_company.key.id())
    if not delivery_types:
        delivery_types = _get_company_info()[1]
        memcache.set('delivery_type_%s' % resto_company.key.id(), delivery_types, time=3600)
    return delivery_types


def get_delivery_zone(zone_key):
    resto_company = RestoCompany.get()
    delivery_zone = memcache.get('delivery_zone_%s_%s' % (resto_company.key.id(), zone_key))
    if not delivery_zone:
        delivery_zone = _get_company_info()[2][zone_key]
        memcache.set('delivery_zone_%s_%s' % (resto_company.key.id(), zone_key), delivery_zone, time=3600)
    return delivery_zone


def get_company_info_dict():
    resto_company = RestoCompany.get()
    info = memcache.get('company_info_%s' % resto_company.key.id())
    if not info:
        info = _get_company_info()[3]
        memcache.set('info_%s' % resto_company.key.id(), info, time=3600)
    return info
