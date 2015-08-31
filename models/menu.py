# coding=utf-8
import logging
import random
from google.appengine.ext import ndb
from methods import fastcounter
from models import STATUS_AVAILABLE, STATUS_CHOICES

SINGLE_MODIFIER = 0
GROUP_MODIFIER = 1


class SingleModifier(ndb.Model):
    INFINITY = 1000

    title = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(default=0)  # в копейках
    min_amount = ndb.IntegerProperty(default=0)
    max_amount = ndb.IntegerProperty(default=0)
    sequence_number = ndb.IntegerProperty(default=0)

    @classmethod
    def get(cls, modifier_id):
        from config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.menu import get_single_modifier_by_id
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(int(modifier_id))
        elif app_kind == RESTO_APP:
            return get_single_modifier_by_id(modifier_id)

    @property
    def float_price(self):  # в рублях
        return float(self.price) / 100.0

    @staticmethod
    def generate_sequence_number():
        fastcounter.incr("category", delta=100, update_interval=1)
        return fastcounter.get_count("category") + random.randint(1, 100)

    @staticmethod
    def get_modifiers_in_order():
        return sorted(SingleModifier.query().fetch(), key=lambda modifier: modifier.sequence_number)

    def get_previous_modifier(self):
        modifiers = self.get_modifiers_in_order()
        index = modifiers.index(self)
        if index == 0:
            return None
        else:
            return modifiers[index - 1]

    def get_next_modifier(self):
        modifiers = self.get_modifiers_in_order()
        index = modifiers.index(self)
        if index == len(modifiers) - 1:
            return None
        else:
            return modifiers[index + 1]

    def dict(self):
        return {
            'modifier_id': str(self.key.id()),
            'title': self.title,
            'price': float(self.price) / 100.0,  # в рублях
            'min': self.min_amount,
            'max': self.max_amount,
            'order': self.sequence_number
        }


class GroupModifierChoice(ndb.Model):
    choice_id = ndb.IntegerProperty()
    choice_id_str = ndb.StringProperty()  # todo: set choice_id to str
    title = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(default=0)  # в копейках
    default = ndb.BooleanProperty(default=False)
    sequence_number = ndb.IntegerProperty()

    @property
    def float_price(self):  # в рублях
        return float(self.price) / 100.0

    @staticmethod
    def generate_id():
        fastcounter.incr("group_choice_id", delta=100, update_interval=1)
        return fastcounter.get_count("group_choice_id") + random.randint(1, 100)

    @classmethod
    def create(cls, title, price):
        choice = cls(choice_id=GroupModifierChoice.generate_id(), title=title, price=price)
        choice.put()
        return choice

    @classmethod
    def get_by_choice_id(cls, choice_id):  # use outside of group_modifier
        return cls.query(cls.choice_id == choice_id).get()

    def get_group_modifier(self):  # use outside of group_modifier
        return GroupModifier.get_modifier_by_choice(self.choice_id)


class GroupModifier(ndb.Model):
    title = ndb.StringProperty(required=True)
    choices = ndb.StructuredProperty(GroupModifierChoice, repeated=True)
    required = ndb.BooleanProperty(default=True)
    sequence_number = ndb.IntegerProperty()

    @classmethod
    def get(cls, modifier_id):
        from config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.menu import get_group_modifier_by_id
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(int(modifier_id))
        elif app_kind == RESTO_APP:
            return get_group_modifier_by_id(modifier_id)

    def get_choice_by_id(self, choice_id):
        from config import Config, AUTO_APP, RESTO_APP
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            choice_id = int(choice_id)
            choices = self.choices
        elif app_kind == RESTO_APP:
            choices = self.get(self.key.id()).choices
        for choice in choices:
            if choice_id == choice.choice_id or choice_id == choice.choice_id_str:
                return choice
        return None

    def generate_choice_sequence_number(self):
        fastcounter.incr("group_modifier_choice_%s" % self.key.id(), delta=100, update_interval=1)
        return fastcounter.get_count("group_modifier_choice_%s" % self.key.id()) + random.randint(1, 100)

    def get_choices_in_order(self):
        return sorted([choice for choice in self.choices], key=lambda choice: choice.sequence_number)

    def get_previous_choice(self, choice):
        choices = self.get_choices_in_order()
        index = choices.index(choice)
        if index == 0:
            return None
        else:
            return choices[index - 1]

    def get_next_choice(self, choice):
        choices = self.get_choices_in_order()
        index = choices.index(choice)
        if index == len(choices) - 1:
            return None
        else:
            return choices[index + 1]

    @classmethod
    def get_modifier_by_choice(cls, choice_id):
        for modifier in cls.query().fetch():
            for choice in modifier.choices:
                if choice.choice_id == choice_id:
                    return modifier
        return None

    @staticmethod
    def generate_sequence_number():
        fastcounter.incr("group_modifier", delta=100, update_interval=1)
        return fastcounter.get_count("group_modifier") + random.randint(1, 100)

    @classmethod
    def get_modifiers_in_order(cls):
        return sorted([modifier for modifier in cls.query().fetch()],
                      key=lambda modifier: modifier.sequence_number)

    def get_previous_modifier(self):
        modifiers = self.get_modifiers_in_order()
        index = modifiers.index(self)
        if index == 0:
            return None
        else:
            return modifiers[index - 1]

    def get_next_modifier(self):
        modifiers = self.get_modifiers_in_order()
        index = modifiers.index(self)
        if index == len(modifiers) - 1:
            return None
        else:
            return modifiers[index + 1]

    def dict(self, product=None):
        choices = [choice for choice in self.choices
                   if product is None or choice.choice_id not in product.group_choice_restrictions]
        return {
            'modifier_id': str(self.key.id()),
            'title': self.title,
            'required': self.required,
            'order': self.sequence_number,
            'choices': [
                {
                    'default': choice.default,
                    'title': choice.title,
                    'price': float(choice.price) / 100.0,  # в рублях
                    'id': str(choice.choice_id) if choice.choice_id else choice.choice_id_str,
                    'order': choice.sequence_number
                } for choice in choices
            ]
        }


class MenuCategory(ndb.Model):
    category = ndb.KeyProperty()  # kind=self, if it is None, that is initial category
    title = ndb.StringProperty(required=True, indexed=False)
    picture = ndb.StringProperty(indexed=False)
    icon = ndb.StringProperty(indexed=False)
    sequence_number = ndb.IntegerProperty()

    @classmethod
    def get_initial_category(cls):
        category = cls.query(MenuCategory.category == None).get()
        if not category:
            category = cls(title=u'Начальная категория')
            category.put()
        return category

    def get_categories(self):
        from config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.menu import get_categories
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            return MenuCategory.query(MenuCategory.category == self.key).fetch()
        elif app_kind == RESTO_APP:
            return get_categories(self)

    def get_items(self, only_available=False):
        from methods.proxy.resto.menu import get_products
        from config import Config, AUTO_APP, RESTO_APP
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            items = MenuItem.query(MenuItem.category == self.key).fetch()
        elif app_kind == RESTO_APP:
            items = get_products(self)
        else:
            items = []
        if only_available:
            for item in items[:]:
                if item.status != STATUS_AVAILABLE:
                    items.remove(item)
        return items

    @staticmethod
    def generate_category_sequence_number():
        fastcounter.incr("category", delta=100, update_interval=1)
        return fastcounter.get_count("category") + random.randint(1, 100)

    @staticmethod
    def get_categories_in_order():
        return sorted(MenuCategory.query().fetch(), key=lambda category: category.sequence_number)

    def get_previous_category(self):
        categories = self.get_categories_in_order()
        index = categories.index(self)
        if index == 0:
            return None
        else:
            return categories[index - 1]

    def get_next_category(self):
        categories = self.get_categories_in_order()
        index = categories.index(self)
        if index == len(categories) - 1:
            return None
        else:
            return categories[index + 1]

    def generate_sequence_number(self):
        fastcounter.incr("category_%s" % self.key.id(), delta=100, update_interval=1)
        return fastcounter.get_count("category_%s" % self.key.id()) + random.randint(1, 100)

    def get_items_in_order(self):
        return sorted(self.get_items(), key=lambda item: item.sequence_number)

    def get_previous(self, item):
        items = self.get_items_in_order()
        if item not in items:
            return None
        index = items.index(item)
        if index == 0:
            return None
        else:
            return items[index - 1]

    def get_next(self, item):
        items = self.get_items_in_order()
        if item not in items:
            return None
        index = items.index(item)
        if index == len(items) - 1:
            return None
        else:
            return items[index + 1]

    def dict(self, venue=None):
        items = []
        for item in self.get_items(only_available=True):
            if not venue:
                items.append(item.dict())
            else:
                if venue.key not in item.restrictions:
                    items.append(item.dict(without_restrictions=True))
        dct = {
            'info': {
                'category_id': str(self.key.id()),
                'title': self.title,
                'pic': self.picture,
                'restrictions': {
                    'venues': []  # todo: update restrictions logic for categories
                },
                'order': self.sequence_number if self.sequence_number else 0
            },
            'items': items,
            'categories': [category.dict(venue) for category in self.get_categories()]
        }
        if venue:
            del dct['info']['restrictions']
        return dct

    @classmethod
    def get_menu_dict(cls, venue=None):
        init_category = cls.get_initial_category()
        category_dicts = []
        for category in init_category.get_categories():
            category_dict = category.dict(venue)
            if category_dict['items'] or category_dict['categories']:
                category_dicts.append(category_dict)
        return category_dicts


class MenuItem(ndb.Model):
    category = ndb.KeyProperty(kind=MenuCategory)
    title = ndb.StringProperty(required=True)
    description = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=False)  # source
    cut_picture = ndb.StringProperty(indexed=False)
    icon = ndb.StringProperty(indexed=False)
    kal = ndb.IntegerProperty(indexed=False)
    weight = ndb.FloatProperty(indexed=False, default=0)
    volume = ndb.FloatProperty(indexed=False, default=0)
    price = ndb.IntegerProperty(default=0, indexed=False)  # в копейках

    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    sequence_number = ndb.IntegerProperty(default=0)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_modifiers = ndb.KeyProperty(kind=GroupModifier, repeated=True)

    restrictions = ndb.KeyProperty(repeated=True)  # kind=Venue (permanent use)
    group_choice_restrictions = ndb.IntegerProperty(repeated=True)  # GroupModifierChoice.choice_id
    stop_list_group_choices = ndb.IntegerProperty(repeated=True)    # GroupModifierChoice.choice_id

    @classmethod
    def get(cls, product_id):
        from config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.menu import get_product_by_id
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(int(product_id))
        elif app_kind == RESTO_APP:
            return get_product_by_id(product_id)

    @property
    def float_price(self):  # в рублях
        return float(self.price) / 100.0

    def dict(self, without_restrictions=False):
        dct = {
            'id': str(self.key.id()),
            'order': self.sequence_number,
            'title': self.title,
            'description': self.description,
            'price':  float(self.price) / 100.0,  # в рублях
            'kal': self.kal,
            'pic': self.picture if not self.cut_picture else self.cut_picture,
            'icon': self.icon,
            'weight': self.weight,
            'volume': self.volume,
            'single_modifiers': [SingleModifier.get(modifier.id()).dict() for modifier in self.single_modifiers],
            'group_modifiers': [GroupModifier.get(modifier.id()).dict(self) for modifier in self.group_modifiers],
            'restrictions': {
                'venues': [str(restrict.id()) for restrict in self.restrictions]
            }
        }
        if without_restrictions:
            del dct['restrictions']
        return dct
