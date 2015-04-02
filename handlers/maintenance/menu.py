__author__ = 'dvpermyakov'

from base import BaseHandler
from models import MenuCategory, MenuItem, STATUS_AVAILABLE, STATUS_UNAVAILABLE, SINGLE_MODIFIER, SingleModifier, GROUP_MODIFIER, GroupModifier, GroupModifierChoice
import logging


class MainMenuHandler(BaseHandler):
    def get(self):
        self.render('/menu/main.html')


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
        picture = self.request.get('picture')
        weight = self.request.get_range('weight')
        volume = self.request.get_range('volume')
        kal = self.request.get_range('kal')

        item = MenuItem(title=title)
        item.description = description
        item.price = price
        item.kal = kal
        item.volume = volume
        item.weight = weight
        item.picture = picture if picture else None
        item.put()
        category.menu_items.append(item.key)
        category.put()
        self.redirect('/mt/menu/item/list?category_id=%s' % category_id)


class SelectProductForModifierHandler(BaseHandler):
    def get(self):
        modifier_type = self.request.get_range('modifier_type')
        modifier = None
        if modifier_type == SINGLE_MODIFIER:
            modifier = SingleModifier.get_by_id(self.request.get_range('modifier_id'))
        elif modifier_type == GROUP_MODIFIER:
            modifier = GroupModifier.get_by_id(self.request.get_range('modifier_id'))
        else:
            self.abort(400)
        products = MenuItem.query().fetch()
        for product in products:
            if modifier_type == SINGLE_MODIFIER:
                if modifier.key in product.single_modifiers:
                    product.has_modifier = True
                else:
                    product.has_modifier = False
            elif modifier_type == GROUP_MODIFIER:
                if modifier.key in product.group_modifiers:
                    product.has_modifier = True
                else:
                    product.has_modifier = False
        self.render('/menu/select_products_modifier.html', **{
            'products': products,
            'modifier': modifier,
            'modifier_type': modifier_type
        })

    def post(self):
        modifier_type = self.request.get_range('modifier_type')
        modifier = None
        if modifier_type == SINGLE_MODIFIER:
            modifier = SingleModifier.get_by_id(self.request.get_range('modifier_id'))
        elif modifier_type == GROUP_MODIFIER:
            modifier = GroupModifier.get_by_id(self.request.get_range('modifier_id'))
        else:
            self.abort(400)

        for product in MenuItem.query().fetch():
            confirmed = bool(self.request.get(str(product.key.id())))
            if modifier_type == SINGLE_MODIFIER:
                found = False
                for single_modifier in product.single_modifiers:
                    if single_modifier == modifier.key:
                        if not confirmed:
                            product.single_modifiers.remove(single_modifier)
                            product.put()
                        found = True
                if not found:
                    if confirmed:
                        product.single_modifiers.append(modifier.key)
                        product.put()
            elif modifier_type == GROUP_MODIFIER:
                found = False
                for group_modifier in product.group_modifiers:
                    if group_modifier == modifier.key:
                        if not confirmed:
                            product.group_modifiers.remove(group_modifier)
                            product.put()
                        found = True
                if not found:
                    if confirmed:
                        product.group_modifiers.append(modifier.key)
                        product.put()
            self.redirect_to('modifiers_list')


class ModifiersForProductHandler(BaseHandler):
    def get(self):
        product = MenuItem.get_by_id(self.request.get('product_id'))
        self.render('/menu/product_modifiers.html', {
            'product': product,
            'single_modifiers': [modifier.get().modifier.get() for modifier in product.single_modifiers],
            'group_modifiers': [modifier.get() for modifier in product.group_modifiers]
        })


class ModifierList(BaseHandler):
    def get(self):
        self.render('/menu/modifiers.html', **{
            'single_modifiers': SingleModifier.query().fetch(),
            'group_modifiers': GroupModifier.query().fetch()
        })


class AddSingleModifierHandler(BaseHandler):
    def get(self):
        self.render('/menu/add_modifier.html')

    def post(self):
        name = self.request.get('name')
        price = self.request.get_range('price')
        min = self.request.get_range('min')
        max = self.request.get_range('max')
        SingleModifier(title=name, price=price, min_amount=min, max_amount=max).put()
        self.redirect_to('modifiers_list')


class AddGroupModifierHandler(BaseHandler):
    def get(self):
        self.render('/menu/add_group_modifier.html')

    def post(self):
        name = self.request.get('name')
        GroupModifier(title=name).put()
        self.redirect_to('modifiers_list')


class AddGroupModifierItemHandler(BaseHandler):
    def get(self, group_modifier_id):
        self.render('/menu/add_modifier.html')

    def post(self, group_modifier_id):
        name = self.request.get('name')
        price = self.request.get_range('price')
        choice = GroupModifierChoice.create(title=name, price=price)
        group_modifier = GroupModifier.get_by_id(int(group_modifier_id))
        group_modifier.choices.append(choice)
        group_modifier.put()
        self.redirect_to('modifiers_list')

