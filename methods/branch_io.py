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
WHATS_APP = 4
SKYPE = 5
TWITTER = 6
INSTAGRAM = 7
OTHER = 8

CHANNELS = [VK, FACEBOOK, SMS, EMAIL, WHATS_APP, SKYPE, TWITTER, INSTAGRAM, OTHER]

CHANNEL_MAP = {
    VK: 'vk',
    FACEBOOK: 'facebook',
    SMS: 'sms',
    EMAIL: 'email',
    WHATS_APP: 'whats app',
    SKYPE: 'skype',
    TWITTER: 'twitter',
    INSTAGRAM: 'instagram',
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


def create_url(share_id, feature, channel, user_agent, recipient=None, alias=None):
    params = {
        'app_id': APP_KEY,
        'data': {
            'phone': recipient.get('phone') if recipient else None,
            'name': recipient.get('name') if recipient else None,
            'share_id': share_id,
            '$desktop_url': DESKTOP_URL,
            '$android_url': ANDROID_URL,
            '$ios_url': IOS_URL
        },
        'alias': alias if alias else None,
        'identity': share_id,
        'tags': [config.BRANCH_IO_TAG, user_agent],
        'campaign': u'Новые пользователи (запуск 03.03.2015)',
        'feature': FEATURE_MAP[feature],
        'channel': CHANNEL_MAP[channel]
    }
    url = '%s%s' % (BASE_URL, '/v1/url')
    response = urlfetch.fetch(url=url, payload=json.dumps(params), method=urlfetch.POST,
                              headers={'Content-Type': 'application/json'}).content
    return json.loads(response)['url']