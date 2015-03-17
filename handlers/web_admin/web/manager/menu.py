# coding: utf-8
from ..base import BaseHandler
from models import MenuCategory, MenuItem, SingleModifier, STATUS_AVAILABLE, STATUS_UNAVAILABLE, GroupModifier, \
    GroupModifierChoice, SINGLE_MODIFIER, GROUP_MODIFIER


class CategoriesHandler(BaseHandler):
    def get(self):
        self.render('/manager/categories.html', **{
            'categories': MenuCategory.query().fetch(),
            'status_map': {
                STATUS_AVAILABLE: u'Доступно',
                STATUS_UNAVAILABLE: u'Недоступно'
            }
        })


class ProductsHandler(BaseHandler):
    def get(self):
        category = MenuCategory.get_by_id(self.request.get_range('category_id'))
        self.render('/manager/products.html', **{
            'products': [item.get() for item in category.menu_items]
        })


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
        self.render('/manager/select_products.html', **{
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
        self.render('/manager/product_modifiers.html', {
            'product': product,
            'single_modifiers': [modifier.get().modifier.get() for modifier in product.single_modifiers],
            'group_modifiers': [modifier.get() for modifier in product.group_modifiers]
        })


class ModifierList(BaseHandler):
    def get(self):
        self.render('/manager/modifiers.html', **{
            'single_modifiers': SingleModifier.query().fetch(),
            'group_modifiers': GroupModifier.query().fetch()
        })


class AddSingleModifierHandler(BaseHandler):
    def get(self):
        self.render('/manager/add_modifier.html')

    def post(self):
        name = self.request.get('name')
        price = self.request.get_range('price')
        SingleModifier(title=name, price=price).put()
        self.redirect_to('modifiers_list')


class AddGroupModifierHandler(BaseHandler):
    def get(self):
        self.render('/manager/add_group_modifier.html')

    def post(self):
        name = self.request.get('name')
        GroupModifier(title=name).put()
        self.redirect_to('modifiers_list')


class AddGroupModifierItemHandler(BaseHandler):
    def get(self, group_modifier_id):
        self.render('/manager/add_modifier.html')

    def post(self, group_modifier_id):
        name = self.request.get('name')
        price = self.request.get_range('price')
        choice = GroupModifierChoice(title=name, price=price)
        choice.put()
        group_modifier = GroupModifier.get_by_id(int(group_modifier_id))
        group_modifier.choices.append(choice)
        group_modifier.put()
        self.redirect_to('modifiers_list')