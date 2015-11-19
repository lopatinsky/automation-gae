# coding=utf-8
from google.appengine.api import memcache
from methods.proxy.doubleb.requests import get_doubleb_menu
from models import MenuItem, MenuCategory, GroupModifierChoice, GroupModifier
from models.proxy.doubleb import DoublebCompany

__author__ = 'dvpermyakov'


GRAINS_ID_START_WITH = 'grains'


def _set_modifiers(items):
    def get_item(new_item, choice):
        for result_item in result_items:
            if result_item.title == title:
                result_item.modifier.choices.append(choice)
                return None
        new_item.modifier = GroupModifier(id='grains_%s' % new_item.key.id(), title=u'Зерна', choices=[choice])
        return new_item

    result_items = []
    for item in items:
        l_index = item.title.find('(')
        r_index = item.title.find(')')
        if l_index == -1 or r_index == -1:
            result_items.append(item)
        else:
            choice_title = item.title[l_index+1:r_index].strip()
            choice = GroupModifierChoice(choice_id=item.key.id(), title=choice_title)
            title = item.title[:l_index].strip()
            item.title = title
            item = get_item(item, choice)
            if item:
                result_items.append(item)
    modifiers = []
    for item in result_items:
        if hasattr(item, 'modifier') and item.modifier:
            modifiers.append(item.modifier)
            item.group_modifiers = [item.modifier.key]
    return result_items, modifiers


def _get_menu():
    menu = memcache.get('doubleb_menu')
    if not menu:
        company = DoublebCompany.get()
        menu = get_doubleb_menu(company)['menu']
        category = MenuCategory(id=667)
        category.category = MenuCategory.get_initial_category().key
        category.title = u'Напитки'
        categories = [category]
        items = []
        for index, item_dict in enumerate(menu[u'Напитки']):
            item = MenuItem(id=int(item_dict['id']))
            item.category = category.key
            item.price = item_dict['price'] * 100
            item.title = item_dict['title']
            item.picture = ''
            item.description = ''
            item.order = index
            item.kal = 0
            item.weight = 0
            items.append(item)
        items, modifiers = _set_modifiers(items)
        menu = categories, items, modifiers
        memcache.set('doubleb_menu', menu, time=3600)
    return menu


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


def get_group_modifier_by_id(modifier_id):
    for modifier in _get_menu()[2]:
        if modifier.key.id() == modifier_id:
            return modifier


def get_product_by_id(product_id):
    for item in _get_menu()[1]:
        if item.key.id() == product_id:
            return item
