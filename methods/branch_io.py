# -*- coding: utf-8 -*-

__author__ = 'dvpermyakov'

from google.appengine.api import urlfetch
import json
from config import config

APP_KEY = '99124067684057799'
BASE_URL = 'https://api.branch.io'
ANDROID_URL = "https://play.google.com/store/apps/details?id=com.empatika.doubleb"
IOS_URL = "https://itunes.apple.com/ru/app/dablbi-kofe-i-caj/id908237281"
DESKTOP_URL = "http://dblb.mobi/"

VK = 0
FACEBOOK = 1
SMS = 2
EMAIL = 3
OTHER = 4

CHANNEL_MAP = {
    VK: 'vk',
    FACEBOOK: 'facebook',
    SMS: 'sms',
    EMAIL: 'email',
    OTHER: 'other'
}

SHARE = 0
INVITATION = 1
GIFT = 2

FEATURE_MAP = {
    SHARE: u'Расскажи друзьям',
    INVITATION: u'Пригласи друга',
    GIFT: u'Подари кружку другу'
}


def create_url(share_id, feature, channel, alias=None):
    params = {
        'app_id': APP_KEY,
        'data': {
            '$og_title': u'Заголовок',
            '$og_description': u'Описание',
            '$og_image_ur': 'http://empatika-doubleb-test.appspot.com/images/shared_image.png',
            '$desktop_url': DESKTOP_URL,
            '$android_url': ANDROID_URL,
            '$ios_url': IOS_URL
        },
        'alias': alias if alias else None,
        'identity': share_id,
        'tags': [config.BRANCH_IO_TAG],
        'campaign': u'Новые пользователи (запуск 03.03.2015)',
        'feature': FEATURE_MAP[feature],
        'channel': CHANNEL_MAP[channel]
    }
    url = '%s%s' % (BASE_URL, '/v1/url')
    response = urlfetch.fetch(url=url, payload=json.dumps(params), method=urlfetch.POST,
                              headers={'Content-Type': 'application/json'}).content

    return response['url']