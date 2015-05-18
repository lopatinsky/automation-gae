# coding:utf-8
__author__ = 'dvpermyakov'

from google.appengine.api import urlfetch
import urllib
import json
import logging


def _parse_collection(collection, kind='house'):  # used only for kind in ['house', 'street']
    if kind not in ['house', 'street']:
        return
    candidates = []
    for item in collection:
        item = item['GeoObject']
        if item['metaDataProperty']['GeocoderMetaData']['kind'] not in kind:
            continue
        address = item['metaDataProperty']['GeocoderMetaData']['AddressDetails']
        address = address['Country']['AdministrativeArea']['SubAdministrativeArea']['Locality']
        city = address['LocalityName']
        if address.get('DependentLocality'):
            address = address['DependentLocality']
        logging.info(address)
        candidates.append({
            'address': {
                'city': city,
                'street': address['Thoroughfare']['ThoroughfareName'].replace(u'улица', '').strip(),
                'home': address['Thoroughfare']['Premise']['PremiseNumber'] if kind == 'house' else None
            },
            'coordinates': {
                'lon': item['Point']['pos'].split(' ')[0],
                'lat': item['Point']['pos'].split(' ')[1],
            }
        })
    return candidates


def get_houses_by_address(city, street, home):
    params = {
        'geocode': ('%s,%s,%s' % (city, street, home)).encode('utf-8'),
        'format': 'json',
        'results': 3
    }
    url = 'http://geocode-maps.yandex.ru/1.x/?%s' % urllib.urlencode(params)
    response = urlfetch.fetch(url)
    response = json.loads(response.content)
    collection = response['response']['GeoObjectCollection']['featureMember']

    return _parse_collection(collection, kind='house')


def get_houses_by_coordinates(lat, lon):
    params = {
        'geocode': '%s,%s' % (lon, lat),
        'format': 'json',
        'kind': 'house',
        'results': 3
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
        'results': 3
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
        'results': 3
    }
    url = 'http://geocode-maps.yandex.ru/1.x/?%s' % urllib.urlencode(params)
    logging.info(url)
    response = urlfetch.fetch(url)
    response = json.loads(response.content)
    collection = response['response']['GeoObjectCollection']['featureMember']

    candidates = _parse_collection(collection, kind='house')
    if not candidates:
        candidates = _parse_collection(collection, kind='street')
    return candidates