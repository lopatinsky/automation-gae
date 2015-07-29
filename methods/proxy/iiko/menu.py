import logging
from config import Config
from models import MenuCategory, STATUS_AVAILABLE, MenuItem
from requests import get_iiko_menu

__author__ = 'dvpermyakov'


def get_menu():
    config = Config.get()
    iiko_company = config.IIKO_COMPANY.get()
    iiko_menu = get_iiko_menu(iiko_company)
    categories = []
    category_items = {}
    for iiko_category in iiko_menu['menu']:
        if not iiko_category['products']:
            continue
        category = MenuCategory()
        category.faked_id = iiko_category['id']
        category.title = iiko_category['name']
        category.picture = iiko_category['image'][0]['imageUrl'] if iiko_category['image'] else ''
        category.status = STATUS_AVAILABLE
        category.sequence_number = iiko_category['order']
        categories.append(category)
        products = []
        for iiko_product in iiko_category['products']:
            product = MenuItem()
            product.faked_id = iiko_product['productId']
            product.status = STATUS_AVAILABLE
            product.title = iiko_product['name']
            product.description = iiko_product['description']
            product.picture = iiko_product['images'][0] if iiko_product['images'] else ''
            product.price = int(iiko_product['price'] * 100)
            product.sequence_number = iiko_product['order']
            products.append(product)
        category_items[category.faked_id] = products
    logging.info(category_items)
    return categories, category_items


def get_categories():
    return get_menu()[0]


def get_products(category):
    logging.info('category = %s' % category)
    return get_menu()[1][category.faked_id]
