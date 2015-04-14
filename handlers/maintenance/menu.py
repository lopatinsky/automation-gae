from google.appengine.ext import ndb
from methods.unique import unique

__author__ = 'dvpermyakov'

from base import BaseHandler
from models import MenuCategory, MenuItem, STATUS_AVAILABLE, STATUS_UNAVAILABLE, SINGLE_MODIFIER, SingleModifier, GROUP_MODIFIER, GroupModifier, GroupModifierChoice, Venue
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

        item = MenuItem(title=self.request.get('title'))
        item.description = self.request.get('description')
        item.price = self.request.get_range('price')
        item.kal = self.request.get_range('kal')
        item.volume = self.request.get_range('volume')
        item.weight = self.request.get_range('weight')
        item.picture = self.request.get('picture') if self.request.get('picture') else None
        item.put()
        category.menu_items.append(item.key)
        category.put()
        self.redirect('/mt/menu/item/list?category_id=%s' % category_id)


class EditMenuItemHandler(BaseHandler):
    def get(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        product_id = self.request.get_range('item_id')
        product = MenuItem.get_by_id(product_id)
        if not product:
            self.abort(400)
        self.render('/menu/add_item.html', product=product, category=category)

    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        product_id = self.request.get_range('product_id')
        item = MenuItem.get_by_id(product_id)
        if not item:
            self.abort(400)

        item.description = self.request.get('description')
        item.price = self.request.get_range('price')
        item.kal = self.request.get_range('kal')
        item.volume = self.request.get_range('volume')
        item.weight = self.request.get_range('weight')
        item.picture = self.request.get('picture') if self.request.get('picture') else None
        item.put()
        self.redirect('/mt/menu/item/list?category_id=%s' % category_id)


class RemoveMenuItemHandler(BaseHandler):
    @staticmethod
    @ndb.transactional(xg=True)
    def delete_item_from_anything(venues, category, item):
        category.menu_items.remove(item.key)
        category.put()
        for venue in venues:
            if item.key in venue.stop_lists:
                venue.stop_lists.remove(item.key)
                venue.put()
        item.key.delete()

    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        item_id = self.request.get_range('item_id')
        item = MenuItem.get_by_id(item_id)
        if not item:
            self.abort(400)
        if item.key not in category.menu_items:
            self.abort(409)
        self.delete_item_from_anything(Venue.query().fetch(), category, item)
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
        categories = MenuCategory.query().fetch()
        for category in categories:
            category.products = []
            for product in category.menu_items:
                product = product.get()
                category.products.append(product)
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
            'categories': categories,
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


class SelectProductForChoiceHandler(BaseHandler):
    def get_products(self, group_modifier, choice):
        products = []
        for product in MenuItem.query().fetch():
            if group_modifier.key in product.group_modifiers:
                products.append(product)
            product.has_choice = choice.choice_id not in product.group_choice_restrictions
        return products

    def get(self):
        choice_id = self.request.get_range('choice_id')
        choice = GroupModifierChoice.get_by_choice_id(choice_id)
        if not choice:
            self.abort(400)
        group_modifier = choice.get_group_modifier()
        if not group_modifier:
            self.abort(400)

        self.render('/menu/select_group_choices.html', **{
            'products': self.get_products(group_modifier, choice),
            'choice': choice
        })

    def post(self):
        choice_id = self.request.get_range('choice_id')
        choice = GroupModifierChoice.get_by_choice_id(choice_id)
        if not choice:
            self.abort(400)
        group_modifier = choice.get_group_modifier()
        if not group_modifier:
            self.abort(400)

        for product in self.get_products(group_modifier, choice):
            confirmed = bool(self.request.get(str(product.key.id())))
            if confirmed and choice.choice_id in product.group_choice_restrictions:
                product.group_choice_restrictions.remove(choice.choice_id)
                product.put()
            if not confirmed and choice.choice_id not in product.group_choice_restrictions:
                product.group_choice_restrictions.append(choice.choice_id)
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
        self.render('/menu/add_modifier.html', **{
            'single_modifier': True
        })

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
        for name in unique(self.request.params.getall('name')):
            if name:
                GroupModifier(title=name).put()
        self.redirect_to('modifiers_list')


class AddGroupModifierItemHandler(BaseHandler):
    def get(self, group_modifier_id):
        self.render('/menu/add_modifier.html', **{
            'group_modifier_choice': True
        })

    def post(self, group_modifier_id):
        name = self.request.get('name')
        prices = unique(self.request.params.getall('price'))

        group_modifier = GroupModifier.get_by_id(int(group_modifier_id))
        for price in prices:
            if not len(price):
                continue
            price = int(price)
            choice = GroupModifierChoice.create(title=name, price=price)
            group_modifier.choices.append(choice)
        group_modifier.put()
        self.redirect_to('modifiers_list')

