# coding=utf-8
import json
from google.appengine.api import memcache
from google.appengine.api.namespace_manager import namespace_manager
from methods.auth import menu_rights_required
from methods.cities import get_company_cities
from methods.images import get_new_image_url, ICON_SIZE
from methods.proxy.resto.menu import reload_menu
from methods.unique import unique
from base import CompanyBaseHandler
from models.config.config import config, RESTO_APP
from models.menu import SINGLE_MODIFIER, GROUP_MODIFIER

__author__ = 'dvpermyakov'

from models import MenuCategory, MenuItem, STATUS_AVAILABLE, STATUS_UNAVAILABLE, SingleModifier, GroupModifier, \
    GroupModifierChoice, Venue
import logging


def _swap_sequence_numbers(first, second):
    if first.sequence_number == second.sequence_number:
        first.sequence_number += 1
    else:
        first.sequence_number, second.sequence_number = second.sequence_number, first.sequence_number


class NoneHandler(CompanyBaseHandler):  # use to erase 404 error
    @menu_rights_required
    def get(self):
        self.redirect('/company/menu/main')


class MainMenuHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        self.render('/menu/main.html')

    def post(self):
        app_kind = config.APP_KIND
        if app_kind == RESTO_APP:
            reload_menu()

        cities = get_company_cities()

        memcache.delete('menu_')
        for city in cities:
            logging.info('menu_%s' % str(city))
            memcache.delete('menu_%s' % str(city))

        self.render('/menu/main.html')


class ListCategoriesHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        venue_id = self.request.get_range('venue_id')
        if venue_id:
            venue = Venue.get_by_id(venue_id)
        else:
            venue = None
        category_id = self.request.get_range('category_id')
        if category_id:
            category = MenuCategory.get_by_id(category_id)
        else:
            category = MenuCategory.get_initial_category()
        categories = sorted(category.get_categories(venue), key=lambda category: category.sequence_number)
        self.render('/menu/categories.html', categories=categories, main_category=category,
                    venues=Venue.query().fetch(), chosen_venue=venue)

    @menu_rights_required
    def post(self):
        logging.info(self.request.POST)
        category_id = self.request.get_range('category_id')
        if category_id:
            category = MenuCategory.get_by_id(category_id)
        else:
            category = MenuCategory.get_initial_category()

        if not category:
            self.abort(400)
            
        for subcategory in category.get_categories():
            subcategory.status = bool(self.request.get(str(subcategory.key.id())))
            subcategory.put()

        self.redirect('/company/menu/category/list?%s' % self.request.query_string)


class UpCategoryHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        previous = category.get_previous_category()
        if not previous:
            self.abort(400)
        _swap_sequence_numbers(previous, category)
        category.put()
        previous.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'category_id': category.key.id(),
            'previous_id': previous.key.id()
        }, separators=(',', ':')))


class DownCategoryHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        next_ = category.get_next_category()
        if not next_:
            self.abort(400)
        _swap_sequence_numbers(category, next_)
        category.put()
        next_.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'category_id': category.key.id(),
            'next_id': next_.key.id()
        }, separators=(',', ':')))


class CreateCategoryHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        main_category_id = self.request.get_range('main_category_id')
        main_category = MenuCategory.get_by_id(main_category_id)
        if not main_category:
            self.abort(400)
        self.render('/menu/add_category.html', main_category=main_category)

    @menu_rights_required
    def post(self):
        main_category_id = self.request.get_range('main_category_id')
        main_category = MenuCategory.get_by_id(main_category_id)
        if not main_category:
            self.abort(400)
        category = MenuCategory(sequence_number=MenuCategory.generate_category_sequence_number(),
                                category=main_category.key)
        category.title = self.request.get('title')
        category.put()
        if self.request.get('image_file') or self.request.get('picture'):
            if self.request.get('image_file'):
                new_url = get_new_image_url('MenuCategory', category.key.id(), image_data=str(self.request.get('image_file')))
            elif self.request.get('picture'):
                new_url = get_new_image_url('MenuCategory', category.key.id(), url=self.request.get('picture'))
            else:
                new_url = None
            if new_url:
                category.picture = new_url
        if category.picture:
            category.icon = get_new_image_url('MenuCategoryIcon', category.key.id(), url=category.picture, size=ICON_SIZE)
        category.put()
        self.redirect_to('mt_category_list')


class EditCategoryHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        self.render('/menu/add_category.html', category=category)

    @menu_rights_required
    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        category.title = self.request.get('title')
        if self.request.get('image_file') or self.request.get('picture'):
            if self.request.get('image_file'):
                new_url = get_new_image_url('MenuCategory', category.key.id(), image_data=str(self.request.get('image_file')))
            elif self.request.get('picture'):
                new_url = get_new_image_url('MenuCategory', category.key.id(), url=self.request.get('picture'))
            else:
                new_url = None
            if new_url:
                category.picture = new_url
        if category.picture:
            category.icon = get_new_image_url('MenuCategoryIcon', category.key.id(), url=category.picture, size=ICON_SIZE)
        category.put()
        self.redirect_to('mt_category_list')


class DeleteCategoryHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        category.key.delete()
        self.redirect_to('mt_category_list')


class ListMenuItemsHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        venue_id = self.request.get_range('venue_id')
        if venue_id:
            venue = Venue.get_by_id(venue_id)
        else:
            venue = None
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        items = category.get_items_in_order(venue)
        self.render('/menu/items.html', items=items, category=category,
                    venues=Venue.query().fetch(), chosen_venue=venue)

    @menu_rights_required
    def post(self):
        logging.info(self.request.POST)
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        for item in category.get_items():
            item.status = bool(self.request.get(str(item.key.id())))
            item.put()
        self.redirect('/company/menu/item/list?category_id=%s' % category_id)


class MenuItemInfoHandler(CompanyBaseHandler):

    STATUS_MAP = {
        STATUS_AVAILABLE: 'avail',
        STATUS_UNAVAILABLE: 'unavail'
    }

    @menu_rights_required
    def get(self):
        item_id = self.request.get_range('item_id')
        item = MenuItem.get_by_id(item_id)
        if not item:
            self.abort(400)
        status = self.STATUS_MAP[item.status]
        self.render('/menu/item_info.html', item=item, status=status)


class AddMenuItemHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        self.render('/menu/add_item.html', category=category)

    @menu_rights_required
    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)

        item = MenuItem(title=self.request.get('title'))
        item.description = self.request.get('description')

        if self.request.get('price'):
            price = float(self.request.get('price'))
            item.price = int(round(price * 100))

        item.kal = self.request.get_range('kal')
        if self.request.get('volume'):
            item.volume = float(self.request.get('volume'))
        if self.request.get('weight'):
            item.weight = float(self.request.get('weight'))
        item.sequence_number = category.generate_sequence_number()
        item.put()  # it is need to get id in saving image
        if self.request.get('image_file') or self.request.get('picture'):
            if self.request.get('image_file'):
                new_url = get_new_image_url('MenuItem', item.key.id(), image_data=str(self.request.get('image_file')))
                if new_url:
                    item.picture = new_url
            elif self.request.get('picture'):
                new_url = get_new_image_url('MenuItem', item.key.id(), url=self.request.get('picture'))
                if new_url:
                    item.picture = new_url
        if item.picture:
            item.icon = get_new_image_url('MenuItemIcon', item.key.id(), url=item.picture, size=ICON_SIZE)
        item.category = category.key
        if not self.request.get('restriction_on'):
            for venue in Venue.query().fetch():
                item.restrictions.append(venue.key)
        item.put()
        self.redirect('/company/menu/item/list?category_id=%s' % category_id)


class EditMenuItemHandler(CompanyBaseHandler):
    @menu_rights_required
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

    @menu_rights_required
    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        product_id = self.request.get_range('product_id')
        item = MenuItem.get_by_id(product_id)
        if not item:
            self.abort(400)
        item.title = self.request.get('title')
        item.description = self.request.get('description')
        if self.request.get('price'):
            price = float(self.request.get('price'))
            item.price = int(round(price * 100))
        else:
            item.price = 0
        item.kal = self.request.get_range('kal')
        if self.request.get('volume') and self.request.get('volume') != 'None':
            item.volume = float(self.request.get('volume'))
        else:
            item.volume = 0
        if self.request.get('weight') and self.request.get('weight') != 'None':
            item.weight = float(self.request.get('weight'))
        else:
            item.weight = 0
        item.picture = None
        item.cut_picture = None
        item.icon = None
        if self.request.get('image_file') or self.request.get('picture'):
            if self.request.get('image_file'):
                new_url = get_new_image_url('MenuItem', item.key.id(), image_data=str(self.request.get('image_file')))
                if new_url:
                    item.picture = new_url
            elif self.request.get('picture'):
                new_url = get_new_image_url('MenuItem', item.key.id(), url=self.request.get('picture'))
                if new_url:
                    item.picture = new_url
        if item.picture:
            item.icon = get_new_image_url('MenuItemIcon', item.key.id(), url=item.picture, size=ICON_SIZE)
        item.put()
        self.redirect('/company/menu/item/list?category_id=%s' % category_id)


class SelectProductForModifierHandler(CompanyBaseHandler):
    @menu_rights_required
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
            for product in category.get_items(only_available=True):
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

    @menu_rights_required
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


class SelectProductForChoiceHandler(CompanyBaseHandler):
    @menu_rights_required
    def get_products(self, group_modifier, choice):
        products = []
        for product in MenuItem.query(MenuItem.status == STATUS_AVAILABLE).fetch():
            if group_modifier.key in product.group_modifiers:
                products.append(product)
            product.has_choice = choice.choice_id not in product.group_choice_restrictions
        return products

    @menu_rights_required
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

    @menu_rights_required
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


class SelectDefaultChoiceHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        modifier_id = self.request.get_range('modifier_id')
        modifier = GroupModifier.get_by_id(modifier_id)
        if not modifier:
            self.abort(400)
        self.render('/menu/select_default_choice.html', **{
            'modifier': modifier,
            'choices': modifier.choices
        })

    @menu_rights_required
    def post(self):
        modifier_id = self.request.get_range('modifier_id')
        modifier = GroupModifier.get_by_id(modifier_id)
        if not modifier:
            self.abort(400)
        choice_id = self.request.get_range('choice_id')
        for choice in modifier.choices:
            choice.default = choice.choice_id == choice_id
        modifier.put()
        self.redirect_to('modifiers_list')


class ModifierList(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        venue_id = self.request.get_range('venue_id')
        if venue_id:
            venue = Venue.get_by_id(venue_id)
        else:
            venue = None
        single_modifier_ids = []
        group_modifier_ids = []
        products = MenuItem.query().fetch()
        for product in products:
            if venue and venue.key in product.restrictions:
                continue
            for modifier in product.group_modifiers:
                if modifier.id not in group_modifier_ids:
                    group_modifier_ids.append(modifier.id())
            for modifier in product.single_modifiers:
                if modifier.id not in single_modifier_ids:
                    single_modifier_ids.append(modifier.id())
        single_modifiers = SingleModifier.query().order(SingleModifier.sequence_number).fetch()
        for single_modifier in single_modifiers:
            single_modifier.products = []
            for product in products:
                if single_modifier.key in product.single_modifiers:
                    single_modifier.products.append(product)
            if single_modifier.key.id() in single_modifier_ids:
                single_modifier.enable = True
            else:
                single_modifier.enable = False
        group_modifiers = GroupModifier.query().order(GroupModifier.sequence_number).fetch()
        for group_modifier in group_modifiers:
            group_modifier.choices = sorted(group_modifier.choices, key=lambda choice: choice.sequence_number)
            group_modifier.products = []
            for product in products:
                if group_modifier.key in product.group_modifiers:
                    group_modifier.products.append(product)
            if group_modifier.key.id() in group_modifier_ids:
                group_modifier.enable = True
            else:
                group_modifier.enable = False
        self.render('/menu/modifiers.html', **{
            'single_modifiers': single_modifiers,
            'group_modifiers': group_modifiers,
            'inf': SingleModifier.INFINITY,
            'venues': Venue.query().fetch(),
            'chosen_venue': venue
        })

    @menu_rights_required
    def post(self):
        for group_modifier in GroupModifier.query().fetch():
            confirmed = bool(self.request.get('required_%s' % group_modifier.key.id()))
            group_modifier.required = confirmed
            group_modifier.put()
        self.redirect('/company/menu/main')


class AddSingleModifierHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        self.render('/menu/add_modifier.html', **{
            'single_modifier': True
        })

    @menu_rights_required
    def post(self):
        name = self.request.get('name')
        if self.request.get('price'):
            price = float(self.request.get('price'))
            price = int(round(price * 100))
        else:
            price = 0
        min_amount = self.request.get_range('min')
        max_amount = self.request.get_range('max')
        if max_amount == 0:
            max_amount = SingleModifier.INFINITY
        modifier = SingleModifier(title=name, price=price, min_amount=min_amount, max_amount=max_amount)
        modifier.sequence_number = SingleModifier.generate_sequence_number()
        modifier.put()
        self.redirect_to('modifiers_list')


class EditSingleModifierHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        single_modifier_id = self.request.get_range('single_modifier_id')
        single_modifier = SingleModifier.get_by_id(single_modifier_id)
        if not single_modifier:
            self.abort(400)
        self.render('/menu/add_modifier.html', **{
            'single_modifier': True,
            'single_modifier_obj': single_modifier
        })

    @menu_rights_required
    def post(self):
        modifier_id = self.request.get_range('modifier_id')
        single_modifier = SingleModifier.get_by_id(modifier_id)
        if not single_modifier:
            self.abort(400)
        single_modifier.title = self.request.get('name')
        if self.request.get('price'):
            price = float(self.request.get('price'))
            single_modifier.price = int(round(price * 100))
        else:
            single_modifier.price = 0
        single_modifier.min_amount = self.request.get_range('min')
        single_modifier.max_amount = self.request.get_range('max')
        single_modifier.put()
        self.redirect_to('modifiers_list')


class UpSingleModifierHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        modifier_id = self.request.get_range('modifier_id')
        modifier = SingleModifier.get_by_id(modifier_id)
        previous = modifier.get_previous_modifier()
        if not previous:
            self.abort(400)
        _swap_sequence_numbers(previous, modifier)
        modifier.put()
        previous.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'modifier_id': modifier.key.id(),
            'previous_id': previous.key.id()
        }, separators=(',', ':')))


class DownSingleModifierHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        modifier_id = self.request.get_range('modifier_id')
        modifier = SingleModifier.get_by_id(modifier_id)
        if not modifier:
            self.abort(400)
        next_ = modifier.get_next_modifier()
        if not next_:
            self.abort(400)
        _swap_sequence_numbers(modifier, next_)
        modifier.put()
        next_.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'modifier_id': modifier.key.id(),
            'next_id': next_.key.id()
        }, separators=(',', ':')))


class AddGroupModifierHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        self.render('/menu/add_group_modifier.html')

    @menu_rights_required
    def post(self):
        for name in unique(self.request.params.getall('name')):
            if name:
                modifier = GroupModifier(title=name)
                modifier.sequence_number = GroupModifier.generate_sequence_number()
                modifier.put()
        self.redirect_to('modifiers_list')


class EditGroupModifierHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        group_modifier_id = self.request.get_range('group_modifier_id')
        group_modifier = GroupModifier.get_by_id(group_modifier_id)
        if not group_modifier:
            self.abort(400)
        self.render('/menu/add_group_modifier.html', **{
            'group_modifier': group_modifier
        })

    @menu_rights_required
    def post(self):
        group_modifier_id = self.request.get_range('group_modifier_id')
        group_modifier = GroupModifier.get_by_id(group_modifier_id)
        if not group_modifier:
            self.abort(400)
        group_modifier.title = self.request.get('name')
        group_modifier.put()
        self.redirect_to('modifiers_list')


class AddGroupModifierItemHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self, group_modifier_id):
        self.render('/menu/add_modifier.html', **{
            'group_modifier_choice': True
        })

    @menu_rights_required
    def post(self, group_modifier_id):
        name = self.request.get('name')
        prices = unique(self.request.params.getall('price'))

        group_modifier = GroupModifier.get_by_id(int(group_modifier_id))
        for price in prices:
            if not len(price):
                continue
            price = float(price)
            price = int(round(price * 100))
            choice = GroupModifierChoice.create(title=name, price=price)
            choice.sequence_number = group_modifier.generate_choice_sequence_number()
            group_modifier.choices.append(choice)
        group_modifier.put()
        self.redirect_to('modifiers_list')


class EditGroupModifierItemHandler(CompanyBaseHandler):
    @menu_rights_required
    def get(self):
        choice_id = self.request.get_range('choice_id')
        choice = GroupModifierChoice.get_by_choice_id(choice_id)
        if not choice:
            self.abort(400)
        self.render('/menu/add_modifier.html', **{
            'choice_obj': choice,
            'group_modifier_choice': True
        })

    @menu_rights_required
    def post(self):
        choice_id = self.request.get_range('modifier_id')
        choice = GroupModifierChoice.get_by_choice_id(choice_id)
        if not choice:
            self.abort(400)
        choice.title = self.request.get('name')
        if self.request.get('price'):
            price = float(self.request.get('price'))
            choice.price = int(round(price * 100))
        else:
            choice.price = 0
        choice.put()
        modifier = GroupModifier.get_modifier_by_choice(choice_id)
        for m_choice in modifier.choices:
            if m_choice.choice_id == choice_id:
                modifier.choices.remove(m_choice)
                modifier.choices.append(choice)
        modifier.put()
        self.redirect_to('modifiers_list')


class UpProductHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        product_id = self.request.get_range('product_id')
        product = MenuItem.get_by_id(product_id)
        if not product:
            self.abort(400)
        previous = category.get_previous(product)
        if not previous:
            self.abort(400)
        _swap_sequence_numbers(previous, product)
        product.put()
        previous.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'product_id': product.key.id(),
            'previous_id': previous.key.id()
        }, separators=(',', ':')))


class DownProductHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        category_id = self.request.get_range('category_id')
        category = MenuCategory.get_by_id(category_id)
        if not category:
            self.abort(400)
        product_id = self.request.get_range('product_id')
        product = MenuItem.get_by_id(product_id)
        if not product:
            self.abort(400)
        next_ = category.get_next(product)
        if not next_:
            self.abort(400)
        _swap_sequence_numbers(product, next_)
        product.put()
        next_.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'product_id': product.key.id(),
            'next_id': next_.key.id()
        }, separators=(',', ':')))


class UpGroupModifierHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        modifier_id = self.request.get_range('modifier_id')
        modifier = GroupModifier.get_by_id(modifier_id)
        previous = modifier.get_previous_modifier()
        if not previous:
            self.abort(400)
        _swap_sequence_numbers(previous, modifier)
        modifier.put()
        previous.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'modifier_id': modifier.key.id(),
            'previous_id': previous.key.id()
        }, separators=(',', ':')))


class DownGroupModifierHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        modifier_id = self.request.get_range('modifier_id')
        modifier = GroupModifier.get_by_id(modifier_id)
        if not modifier:
            self.abort(400)
        next_ = modifier.get_next_modifier()
        if not next_:
            self.abort(400)
        _swap_sequence_numbers(modifier, next_)
        modifier.put()
        next_.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'modifier_id': modifier.key.id(),
            'next_id': next_.key.id()
        }, separators=(',', ':')))


class UpGroupModifierChoiceHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        key = self.request.get('key')
        choice_id = int(key.split('_')[0])
        modifier_id = int(key.split('_')[1])
        modifier = GroupModifier.get_by_id(modifier_id)
        if not modifier:
            self.abort(400)
        choice = modifier.get_choice_by_id(choice_id)
        if not choice:
            self.abort(400)
        previous = modifier.get_previous_choice(choice)
        if not previous:
            self.abort(400)
        _swap_sequence_numbers(previous, choice)
        modifier.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True
        }, separators=(',', ':')))


class DownGroupModifierChoiceHandler(CompanyBaseHandler):
    @menu_rights_required
    def post(self):
        key = self.request.get('key')
        choice_id = int(key.split('_')[0])
        modifier_id = int(key.split('_')[1])
        modifier = GroupModifier.get_by_id(modifier_id)
        if not modifier:
            self.abort(400)
        choice = modifier.get_choice_by_id(choice_id)
        if not choice:
            self.abort(400)
        next_ = modifier.get_next_choice(choice)
        if not next_:
            self.abort(400)
        _swap_sequence_numbers(choice, next_)
        modifier.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True
        }, separators=(',', ':')))