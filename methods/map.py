# coding:utf-8

__author__ = 'dvpermyakov'

from google.appengine.api import urlfetch
import urllib
import json
import logging
from config import config


MAX_RESULT = 25


def _parse_collection(collection, kind='house', city_request=None):
    if kind not in ['house', 'street']:
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
        if not address.get('Thoroughfare'):
            continue
        candidate_append = False
        street = address['Thoroughfare']['ThoroughfareName'].replace(u'улица', '').strip()
        if kind == 'street':
            if street not in streets:
                streets.append(street)
                candidate_append = True
        else:
            candidate_append = True
        if candidate_append:
            candidates.append({
                'address': {
                    'country': country['CountryName'],
                    'city': city,
                    'street': street,
                    'home': address['Thoroughfare']['Premise']['PremiseNumber'] if kind == 'house' else None
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


def get_houses_by_address(city, street, home):
    params = {
        'geocode': ('%s,%s,%s' % (city, street, home)).encode('utf-8'),
        'format': 'json',
        'results': MAX_RESULT
    }
    url = 'http://geocode-maps.yandex.ru/1.x/?%s' % urllib.urlencode(params)
    logging.info(url)
    response = urlfetch.fetch(url)
    response = json.loads(response.content)
    collection = response['response']['GeoObjectCollection']['featureMember']

    return _parse_collection(collection, kind='house', city_request=city)


def get_houses_by_coordinates(lat, lon):
    params = {
        'geocode': '%s,%s' % (lon, lat),
        'format': 'json',
        'kind': 'house',
        'results': MAX_RESULT
    }
    url = 'http://geocode-maps.yandex.ru/1.x/?%s' % urllib.urlencode(params)
    logging.info(url)
    response = urlfetch.fetch(url)
    response = json.loads(response.content)
    collection = response['response']['GeoObjectCollection']['featureMember']

    return _parse_collection(collection, kind='house')


def get_streets_by_address(city, street):
    params = {
        'geocode': ('%s,%s' % (city, street)).encode('utf-8'),
        'format': 'json',
        'results': MAX_RESULT
    }
    url = 'http://geocode-maps.yandex.ru/1.x/?%s' % urllib.urlencode(params)
    logging.info(url)
    response = urlfetch.fetch(url)
    response = json.loads(response.content)
    collection = response['response']['GeoObjectCollection']['featureMember']

    return _parse_collection(collection, kind='street')


def get_streets_or_houses_by_address(city, street):
    params = {
        'geocode': ('%s,%s' % (city, street)).encode('utf-8'),
        'format': 'json',
        'results': MAX_RESULT
    }
    url = 'http://geocode-maps.yandex.ru/1.x/?%s' % urllib.urlencode(params)
    logging.info(url)
    response = urlfetch.fetch(url)
    response = json.loads(response.content)
    collection = response['response']['GeoObjectCollection']['featureMember']

    candidates = _parse_collection(collection, kind='house', city_request=city)
    if not candidates:
        candidates = _parse_collection(collection, kind='street', city_request=city)
    return candidates