import logging
from google.appengine.api import memcache, namespace_manager
from google.appengine.ext import ndb
from models import MenuCategory, MenuItem, GroupModifier, GroupModifierChoice, SingleModifier
from models.proxy.resto import RestoCompany
from requests import get_resto_menu

__author__ = 'dvpermyakov'

_global_resto_menu_cache = {}


def __get_group_modifiers(resto_modifiers):
    group_modifiers = {}
    for resto_modifier in resto_modifiers:
        if not resto_modifier.get('groupId'):
            continue
        modifier = GroupModifier(id=resto_modifier['groupId'])
        modifier.title = resto_modifier['name']
        modifier.required = resto_modifier['minAmount'] != 0
        modifier.choices = []
        for resto_choice in resto_modifier['items']:
            choice = GroupModifierChoice(choice_id_str=resto_choice['id'])
            choice.title = resto_choice['name']
            choice.price = int(resto_choice['price'] * 100)
            modifier.choices.append(choice)
        group_modifiers[modifier.key] = modifier
    return group_modifiers


def __get_single_modifiers(resto_modifiers):
    single_modifiers = {}
    for resto_modifier in resto_modifiers:
        modifier = SingleModifier(id=resto_modifier['id'])
        modifier.title = resto_modifier['name']
        modifier.price = int(resto_modifier['price'] * 100)
        modifier.min_amount = resto_modifier['minAmount']
        modifier.max_amount = resto_modifier['maxAmount']
        single_modifiers[modifier.key] = modifier
    return single_modifiers


def __get_products(category, resto_products):
    products = []
    group_modifiers = {}
    single_modifiers = {}
    for resto_product in resto_products:
        product = MenuItem(id=resto_product['productId'])
        product.category = category.key
        product.title = resto_product['name']
        product.description = resto_product['description']
        product.weight = resto_product['weight'] * 1000
        product.kal = int(resto_product['energyAmount'] or 0)
        product.picture = resto_product['images'][0] if resto_product['images'] else ''
        product.price = int(resto_product['price'] * 100)
        product.sequence_number = resto_product['order']
        products.append(product)
        product_group_modifiers = __get_group_modifiers(resto_product['modifiers'])
        product.group_modifiers = product_group_modifiers.keys()
        group_modifiers.update(product_group_modifiers)
        product_single_modifiers = __get_single_modifiers(resto_product['single_modifiers'])
        product.single_modifiers = product_single_modifiers.keys()
        single_modifiers.update(product_single_modifiers)
    return products, group_modifiers, single_modifiers


def __get_categories(parent_category, resto_categories):
    categories = []
    products = {}
    group_modifiers = {}
    single_modifiers = {}
    for resto_category in resto_categories:
        category = MenuCategory(id=resto_category['id'])
        category.category = parent_category.key
        category.title = resto_category['name']
        category.picture = resto_category['image'][0]['imageUrl'] if resto_category['image'] else ''
        category.sequence_number = resto_category['order']
        if resto_category['children']:
            child_categories, child_products, child_group_modifiers, child_single_modifiers = \
                __get_categories(category, resto_category['children'])
            categories.extend(child_categories)
            products.update(child_products)
            group_modifiers.update(child_group_modifiers)
            single_modifiers.update(child_single_modifiers)
        if resto_category['products']:
            category_products, product_group_modifiers, product_single_modifiers = \
                __get_products(category, resto_category['products'])
            products[category.key] = category_products
            group_modifiers.update(product_group_modifiers)
            single_modifiers.update(product_single_modifiers)
        categories.append(category)
    return categories, products, group_modifiers, single_modifiers


def _get_menu(force_reload=False):
    ns = namespace_manager.get_namespace()
    menu = _global_resto_menu_cache.get(ns)
    if not menu or force_reload:
        logging.debug("Not found in instance cache, trying memcache")
        menu = memcache.get('resto_menu')
        if not menu or force_reload:
            logging.debug("Not found in memcache, reloading from resto")
            resto_company = RestoCompany.get()
            resto_menu = get_resto_menu(resto_company)
            init_category = MenuCategory.get_initial_category()
            menu = __get_categories(init_category, resto_menu['menu'])
            memcache.set("resto_menu", menu, time=3600)
        _global_resto_menu_cache[ns] = menu
    return menu


def reload_menu():
    _get_menu(force_reload=True)


def get_categories(parent_category):
    categories = []
    for category in _get_menu()[0]:
        if category.category == parent_category.key:
            categories.append(category)
    return categories


def get_products(category):
    return _get_menu()[1].get(category.key, [])


def get_product_by_id(product_id):
    for products in _get_menu()[1].values():
        for product in products:
            if product.key.id() == product_id:
                return product


def get_group_modifier_by_id(modifier_id):
    modifier_key = ndb.Key(GroupModifier, modifier_id)
    return _get_menu()[2][modifier_key]


def get_single_modifier_by_id(modifier_id):
    modifier_key = ndb.Key(SingleModifier, modifier_id)
    return _get_menu()[3][modifier_key]
