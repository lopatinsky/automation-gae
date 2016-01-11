# coding: utf-8
import logging
import json

from google.appengine.api import urlfetch

BASE_URL = 'https://api.branch.io'

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
    from models.config.config import config

    params = {
        'branch_key': config.BRANCH_API_KEY,
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
        'campaign': config.APP_NAME,
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


def create_app_key(user_id, app_name, dev_name, dev_email):
    params = {
        'user_id': user_id,
        'app_name': app_name,
        'dev_name': dev_name,
        'dev_email': dev_email
    }
    url = '%s%s' % (BASE_URL, '/v1/app')
    response = urlfetch.fetch(url=url, payload=json.dumps(params), method=urlfetch.POST,
                              headers={'Content-Type': 'application/json'}).content

    logging.info(response)

    branch_key = json.loads(response)['branch_key']
    branch_secret = json.loads(response)['branch_secret']

    return branch_key, branch_secret
