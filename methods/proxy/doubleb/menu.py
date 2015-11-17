# coding=utf-8
from methods.proxy.doubleb.requests import get_doubleb_menu
from models import MenuItem, MenuCategory
from models.proxy.doubleb import DoublebCompany

__author__ = 'dvpermyakov'


def _get_menu():
    company = DoublebCompany.get()
    menu = get_doubleb_menu(company)['menu']
    category = MenuCategory(id=1)
    category.category = MenuCategory.get_initial_category().key
    category.title = u'Напитки'
    items = []
    for index, item_dict in enumerate(menu[u'Напитки']):
        item = MenuItem(id=item_dict['id'])
        item.category = category.key
        item.price = item_dict['price'] * 100
        item.title = item_dict['title']
        item.picture = ''
        item.description = ''
        item.order = index
        item.kal = 0
        item.weight = 0
        items.append(item)
    categories = [category]
    return categories, items


def get_categories(parent):
    if parent.key.id() == MenuCategory.get_initial_category().key.id():
        return _get_menu()[0]
    else:
        return []


def get_items(category):
    items = []
    for item in _get_menu()[1]:
        if item.category.id() == category.key.id():
            items.append(item)
    return items
