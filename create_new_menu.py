# coding=utf-8
from google.appengine.ext import ndb

from models import MenuCategory, MenuItem, STATUS_UNAVAILABLE


def do():
    category = MenuCategory(id=2, title=u"Напитки", status=STATUS_UNAVAILABLE)

    start_id = 100
    items = []

    def _next_id():
        last_id = items[-1].key.id() if items else start_id
        return last_id + 1

    def _add_item(title, price, beans=()):
        if not beans:
            items.append(MenuItem(id=_next_id(), title=title, price=price))
        else:
            for bean in beans:
                _add_item("%s (%s)" % (title, bean), price)

    std_beans = u"Сальвадор,Кения,Эфиопия,Гондурас,Коста-Рика".split(',')

    _add_item(u"Аэропресс", 150, std_beans)
    _add_item(u"Харио", 150, std_beans)
    _add_item(u"Лунго", 150, std_beans)
    _add_item(u"Двойной эспрессо", 150)

    _add_item(u"Айс-латте", 200)
    _add_item(u"Капучино", 200)

    _add_item(u"Ванильный раф", 250)
    _add_item(u"Цитрусовый раф", 250)
    _add_item(u"Какао", 250)
    _add_item(u"Латте", 250)
    _add_item(u"Большой капучино", 250)

    _add_item(u"Лавандовый раф", 350)
    _add_item(u"Латте крем-брюле", 350)
    _add_item(u"Латте базилик", 350)
    _add_item(u"Латте груша-бадьян", 350)
    _add_item(u"Латте шалфей", 350)
    _add_item(u"Клюквенный чай", 350)
    _add_item(u"Чай огурец с ромашкой", 350)

    category.menu_items = [item.key for item in items]
    ndb.put_multi([category] + items)
