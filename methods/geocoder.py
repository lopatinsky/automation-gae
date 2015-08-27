# coding:utf-8

__author__ = 'dvpermyakov'

from google.appengine.api import urlfetch
import urllib
import json
import logging
from config import config

BASE_URL = 'http://geocode-maps.yandex.ru/1.x/'
MAX_RESULT = 15

CITY = 'locality'
DISTRICT = 'district'
STREET = 'street'
HOUSE = 'house'
CHOICES = (CITY, DISTRICT, STREET, HOUSE)


def _parse_collection(collection, kind=HOUSE, city_request=None):
    if kind not in CHOICES:
        return
    candidates = []
    streets = []
    for item in collection:
        item = item['GeoObject']
        if item['metaDataProperty']['GeocoderMetaData']['kind'] not in kind:
            continue
        address_details = item['metaDataProperty']['GeocoderMetaData']['AddressDetails']
        country = address_details['Country']
        if u''.join([country['CountryName']]) not in (config.COUNTRIES if config.COUNTRIES else [u'Россия']):
            continue
        if not country.get('AdministrativeArea'):
            continue
        address = country['AdministrativeArea']['SubAdministrativeArea']['Locality']
        city = address.get('LocalityName')
        if city_request and city != city_request:
            continue
        if address.get('DependentLocality'):
            address = address['DependentLocality']
        if address.get('Thoroughfare'):
            street = address['Thoroughfare']['ThoroughfareName'].replace(u'улица', '').strip()
            home = address['Thoroughfare']['Premise']['PremiseNumber'] if kind == HOUSE else None
        else:
            if kind in [STREET, HOUSE]:
                continue
            street = None
            home = None
        candidate_append = False
        if kind == STREET:
            if street not in streets:
                streets.append(street)
                candidate_append = True
        else:
            candidate_append = True
        if candidate_append:
            candidates.append({
                'address': {
                    'country': country['CountryName'],
                    'area': address.get('DependentLocalityName'),
                    'city': city,
                    'street': street,
                    'home': home
                },
                'coordinates': {
                    'lon': item['Point']['pos'].split(' ')[0],
                    'lat': item['Point']['pos'].split(' ')[1],
                },
                'address_str': item['metaDataProperty']['GeocoderMetaData']['text'],
                'global_address_str': item['description'],
                'local_address_str': item['name']
            })
    return candidates


def _get_collection(params):
    url = '%s?%s' % (BASE_URL, urllib.urlencode(params))
    logging.info(url)
    try:
        response = urlfetch.fetch(url, deadline=3)
        response = json.loads(response.content)
    except Exception as e:
        logging.warning(str(e))
        response = None
    if response:
        return response['response']['GeoObjectCollection']['featureMember']
    else:
        return None


def get_houses_by_address(city, street, home):
    collection = _get_collection({
        'geocode': ('%s,%s,%s' % (city, street, home)).encode('utf-8'),
        'format': 'json',
        'results': MAX_RESULT
    })
    if collection:
        return _parse_collection(collection, kind=HOUSE, city_request=city)
    else:
        return []


def get_houses_by_coordinates(lat, lon):
    collection = _get_collection({
        'geocode': '%s,%s' % (lon, lat),
        'format': 'json',
        'kind': HOUSE,
        'results': MAX_RESULT
    })
    if collection:
        return _parse_collection(collection, kind=HOUSE)
    else:
        return []


def get_cities_by_coordinates(lat, lon):
    collection = _get_collection({
        'geocode': '%s,%s' % (lon, lat),
        'format': 'json',
        'kind': CITY,
        'results': MAX_RESULT
    })
    if collection:
        return _parse_collection(collection, kind=CITY)
    else:
        return []


def get_areas_by_coordinates(lat, lon):
    collection = _get_collection({
        'geocode': '%s,%s' % (lon, lat),
        'format': 'json',
        'kind': DISTRICT,
        'results': MAX_RESULT
    })
    if collection:
        return _parse_collection(collection, kind=DISTRICT)
    else:
        return []


def get_streets_by_address(city, street):
    collection = _get_collection({
        'geocode': ('%s,%s' % (city, street)).encode('utf-8'),
        'format': 'json',
        'results': MAX_RESULT
    })
    if collection:
        return _parse_collection(collection, kind=STREET)
    else:
        return []


def get_streets_or_houses_by_address(city, street):
    collection = _get_collection({
        'geocode': ('%s,%s' % (city, street)).encode('utf-8'),
        'format': 'json',
        'results': MAX_RESULT
    })
    if collection:
        candidates = _parse_collection(collection, kind=HOUSE, city_request=city)
        if not candidates:
            candidates = _parse_collection(collection, kind=STREET, city_request=city)
        return candidates
    else:
        return []