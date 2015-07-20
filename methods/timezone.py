import json
import logging
import urllib
from google.appengine.api import urlfetch

__author__ = 'dvpermyakov'

from methods.rendering import timestamp
from datetime import datetime

API_KEY = 'AIzaSyB5fTi3mO6MiLNoPbbaU6UPXS9fogZ4lZY'
BASE_URL = 'https://maps.googleapis.com/maps/api/timezone/json'


def get_time_zone(lat, lon):
    params = {
        'location': '%s,%s' % (lat, lon),
        'timestamp': timestamp(datetime.utcnow()),
        'key': API_KEY
    }
    url = '%s?%s' % (BASE_URL, urllib.urlencode(params))
    logging.info(url)
    response = urlfetch.fetch(url)
    response = json.loads(response.content)
    if response.get('status') == 'OK':
        return {
            'offset': response['rawOffset'] / 3600,
            'name': response['timeZoneId']
        }