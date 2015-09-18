import logging
from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, MenuItem
from models.specials import Subscription, SubscriptionMenuItem

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
    logging.info('amount in method %s' % amount)
    return amount
