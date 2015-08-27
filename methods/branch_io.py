# coding: utf-8
import logging
from google.appengine.api import urlfetch
import json

BASE_URL = 'https://api.branch.io'
BRANCH_API_KEY = '155014419024204427'


VK = 0
FACEBOOK = 1
SMS = 2
EMAIL = 3
WHATS_APP = 4
SKYPE = 5
TWITTER = 6
INSTAGRAM = 7
OTHER = 8

CHANNELS = (VK, FACEBOOK, SMS, EMAIL, WHATS_APP, SKYPE, TWITTER, INSTAGRAM, OTHER)

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

FEATURE_CHOICES = (SHARE, INVITATION, GIFT)

FEATURE_MAP = {
    SHARE: u'Расскажи друзьям',
    INVITATION: u'Пригласи друга',
    GIFT: u'Подари другу'
}


def create_url(share_id, feature, channel, user_agent, custom_tags=None, recipient=None, alias=None):
    from config import Config
    config = Config.get()
    params = {
        'app_id': BRANCH_API_KEY,
        'data': {
            'phone': recipient.get('phone') if recipient else None,
            'name': recipient.get('name') if recipient else None,
            'share_id': share_id,
            '$desktop_url': config.RBCN_MOBI,
            '$android_url': config.RBCN_MOBI,
            '$ios_url': config.RBCN_MOBI,
        },
        'alias': alias if alias else None,
        'identity': share_id,
        'tags': [user_agent],
        'feature': FEATURE_MAP[feature],
        'channel': CHANNEL_MAP[channel]
    }
    if custom_tags:
        for item in custom_tags.items():
            params['tags'].append("%s__%s" % item)
    url = '%s%s' % (BASE_URL, '/v1/url')
    logging.info(url)
    response = urlfetch.fetch(url=url, payload=json.dumps(params), method=urlfetch.POST,
                              headers={'Content-Type': 'application/json'}).content
    logging.info(response)
    return json.loads(response)['url']
