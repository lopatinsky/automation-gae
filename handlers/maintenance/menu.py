__author__ = 'dvpermyakov'

from base import BaseHandler
from models import MenuCategory, MenuItem, STATUS_AVAILABLE, STATUS_UNAVAILABLE
import logging


class ListCategoriesHandler(BaseHandler):
    def get(self):
        categories = MenuCategory.query().fetch()
        self.render('/menu/categories.html', categories=categories)


class CreateCategoryHandler(BaseHandler):
    def get(self):
        self.render('/menu/add_category.html')

    def post(self):
        title = self.request.get('title')
        MenuCategory(title=title).put()
        self.redirect_to('mt_category_list')


class ListMenuItemsHandler(BaseHandler):
    def get(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        items = [item.get() for item in category.menu_items]
        self.render('/menu/items.html', items=items, category=category)

    def post(self):
        logging.info(self.request.POST)
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        for item in category.menu_items:
            item = item.get()
            item.status = bool(self.request.get(str(item.key.id())))
            item.put()
        self.redirect('/mt/menu/item/list?category_id=%s' % category_id)


class MenuItemInfoHandler(BaseHandler):

    STATUS_MAP = {
        STATUS_AVAILABLE: 'avail',
        STATUS_UNAVAILABLE: 'unavail'
    }

    def get(self):
        item_id = self.request.get_range('item_id')
        item = MenuItem.get_by_id(item_id)
        if not item:
            self.abort(400)
        status = self.STATUS_MAP[item.status]
        self.render('/menu/item_info.html', item=item, status=status)


class AddMenuItemHandler(BaseHandler):
    def get(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        self.render('/menu/add_item.html', category=category)

    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        title = self.request.get('title')
        description = self.request.get('description')
        price = self.request.get_range('price')
        cost_price = self.request.get_range('cost_price')

        item = MenuItem(title=title)
        item.description = description
        item.price = price
        item.cost_price = cost_price
        item.put()
        category.menu_items.append(item.key)
        category.put()
        self.redirect('/mt/menu/item/list?category_id=%s' % category_id)