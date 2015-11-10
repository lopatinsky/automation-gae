from datetime import datetime, timedelta
from google.appengine.ext.deferred import deferred
from models import STATUS_AVAILABLE, MenuCategory, Order, MenuItem, STATUS_UNAVAILABLE
from models.config.config import Config
from models.config.hit import HIT_SEQUENCE_NUMBER

__author__ = 'dvpermyakov'


def include_hit_category(menu_dict):
    config = Config.get()
    if config.HIT_MODULE and config.HIT_MODULE.status == STATUS_AVAILABLE:
        module = config.HIT_MODULE
        category_dict = MenuCategory(id='hit_category', title=module.title, picture=module.picture,
                                     sequence_number=HIT_SEQUENCE_NUMBER).dict()
        category_dict['items'] = [item.dict() for item in module.get_items()]
        if category_dict['items']:
            menu_dict.append(category_dict)


def _update_item_rating(orders, item):
    amount = 0
    for order in orders:
        for item_detail in order.item_details:
            if item_detail.item == item.key:
                amount += 1
                break
    item.rating = float(amount) / len(orders)
    item.put()


def _update_items_rating(orders):
    for item in MenuItem.query(MenuItem.status == STATUS_AVAILABLE).fetch():
        deferred.defer(_update_item_rating, orders, item)
    for item in MenuItem.query(MenuItem.status == STATUS_UNAVAILABLE).fetch():
        item.rating = 0.0
        item.put()


def update_ratings():
    config = Config.get()
    if config.HIT_MODULE and config.HIT_MODULE.status == STATUS_AVAILABLE:
        module = config.HIT_MODULE
        last = datetime.utcnow() - timedelta(days=module.consider_days)
        orders = Order.query(Order.date_created > last).fetch()
        if orders:
            deferred.defer(_update_items_rating, orders)


def update_hit_category():
    config = Config.get()
    if config.HIT_MODULE and config.HIT_MODULE.status == STATUS_AVAILABLE:
        module = config.HIT_MODULE
        items = []
        for item in MenuItem.query().order(-MenuItem.rating).fetch():
            if len(items) >= module.max_item_amount - len(module.cunning_items):
                break
            if item.status == STATUS_UNAVAILABLE:
                continue
            if item.rating < module.min_item_rating:
                break
            items.append(item.key)
        items.extend(module.cunning_items)
        module.items = items
        config.put()
