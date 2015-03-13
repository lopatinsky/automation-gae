from ..base import BaseHandler
from models import MenuCategory, MenuItem, SingleModifier


class CategoriesHandler(BaseHandler):
    def get(self):
        self.render('/manager/categories.html', **{
            'categories': MenuCategory.query().fetch()
        })


class ProductsHandler(BaseHandler):
    def get(self):
        category = MenuCategory.get_by_id(self.request.get('category_id'))
        self.render('/manager/products.html', category=category)


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
        self.render('')


class AddSingleModifierHandler(BaseHandler):
    def get(self):
        self.render('/manager/add_modifier.html')

    def post(self):
        name = self.request.get('name')
        price = self.request.get('price')

        SingleModifier(name=name, price=price).put()