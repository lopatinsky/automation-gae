from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, MenuItem
from models.config.config import config
from models.subscription import Subscription, SubscriptionMenuItem

__author__ = 'dvpermyakov'


def get_subscription(client):
    subscription = Subscription.query(Subscription.client == client.key, Subscription.status == STATUS_AVAILABLE).get()
    return subscription


def get_subscription_menu_item(item_dict):
    item_id = item_dict.get('item_id')
    if not item_id:
        item_id = item_dict.get('item').key.id()
    item_id = int(item_id)
    return SubscriptionMenuItem.query(SubscriptionMenuItem.item == ndb.Key(MenuItem, item_id)).get()


def get_amount_of_subscription_items(item_dicts):
    amount = 0
    for item_dict in item_dicts:
        menu_item = get_subscription_menu_item(item_dict)
        if menu_item:
            amount += item_dict['quantity']
    return amount


def get_subscription_category_dict():
    module = config.SUBSCRIPTION_MODULE
    if module and module.status:
        return True, {
            'info': {
                'category_id': str(1),
                'title': module.menu_title,
                'pic': '',
                'restrictions': {
                    'venues': []  # todo: update restrictions
                },
                'order': 100100100
            },
            'items': [item.dict() for item in SubscriptionMenuItem.query(SubscriptionMenuItem.status == STATUS_AVAILABLE).fetch()],
            'categories': []
        }
    return False, None
