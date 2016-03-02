# coding=utf-8
import logging
import random
from google.appengine.ext import ndb
from methods import fastcounter
from models import STATUS_AVAILABLE, STATUS_CHOICES

SINGLE_MODIFIER = 0
GROUP_MODIFIER = 1


class PriceBase(ndb.Model):
    price = ndb.IntegerProperty(default=0)
    venue_prices = ndb.JsonProperty(default={})

    @property
    def float_price(self):  # в рублях
        return float(self.price) / 100.0

    def price_for_venue(self, venue_id):
        return self.venue_prices.get(str(venue_id), self.price)

    def float_price_for_venue(self, venue_id):
        return float(self.price_for_venue(venue_id)) / 100.0

    @property
    def venue_price_dicts(self):
        return [
            {'venue': venue_id, 'price': price / 100.0}
            for venue_id, price in self.venue_prices.iteritems()
        ]


class SingleModifier(PriceBase):
    INFINITY = 1000

    title = ndb.StringProperty(required=True)
    min_amount = ndb.IntegerProperty(default=0)
    max_amount = ndb.IntegerProperty(default=0)
    sequence_number = ndb.IntegerProperty(default=0)

    @classmethod
    def get(cls, modifier_id):
        from models.config.config import config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.menu import get_single_modifier_by_id
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(int(modifier_id))
        elif app_kind == RESTO_APP:
            return get_single_modifier_by_id(modifier_id)

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

    def dict(self, venue=None):
        dct = {
            'modifier_id': str(self.key.id()),
            'title': self.title,
            'price': self.float_price_for_venue(venue.key.id()) if venue else self.float_price,
            'min': self.min_amount,
            'max': self.max_amount,
            'order': self.sequence_number
        }
        if not venue:
            dct['prices'] = self.venue_price_dicts
        return dct


class GroupModifierChoice(PriceBase):
    choice_id = ndb.IntegerProperty()
    choice_id_str = ndb.StringProperty()  # todo: set choice_id to str
    title = ndb.StringProperty(required=True)
    default = ndb.BooleanProperty(default=False)
    sequence_number = ndb.IntegerProperty()

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
        from models.config.config import config, AUTO_APP, RESTO_APP, DOUBLEB_APP
        from methods.proxy.resto.menu import get_group_modifier_by_id as resto_get_group_modifier_by_id
        from methods.proxy.doubleb.menu import get_group_modifier_by_id as doubleb_get_group_modifier_by_id
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(int(modifier_id))
        elif app_kind == RESTO_APP:
            return resto_get_group_modifier_by_id(modifier_id)
        elif app_kind == DOUBLEB_APP:
            return doubleb_get_group_modifier_by_id(modifier_id)

    def get_choice_by_id(self, choice_id):
        from models.config.config import config, AUTO_APP, RESTO_APP, DOUBLEB_APP
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            choice_id = int(choice_id)
            choices = self.choices
        elif app_kind in [RESTO_APP, DOUBLEB_APP]:
            if app_kind == DOUBLEB_APP:
                choice_id = int(choice_id)
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

    def dict(self, product=None, venue=None):
        choices = [choice for choice in self.choices
                   if product is None or choice.choice_id not in product.group_choice_restrictions]
        if self.required and choices:
            found = False
            suit_choice = choices[0]
            for choice in choices:
                if choice.default:
                    found = True
                if suit_choice.price > choice.price:
                    suit_choice = choice
            if not found:
                suit_choice.default = True
        choices_dicts = []
        for choice in choices:
            choice_dct = {
                'default': choice.default if choice.default else None,
                'title': choice.title,
                'price': choice.float_price_for_venue(venue.key.id()) if venue else choice.float_price,
                'id': str(choice.choice_id) if choice.choice_id else choice.choice_id_str,
                'order': choice.sequence_number
            }
            if not venue:
                choice_dct['prices'] = choice.venue_price_dicts
            choices_dicts.append(choice_dct)
        return {
            'modifier_id': str(self.key.id()),
            'title': self.title,
            'required': self.required,
            'order': self.sequence_number,
            'choices': choices_dicts
        }


class MenuCategory(ndb.Model):
    category = ndb.KeyProperty()  # kind=self, if it is None, that is initial category
    title = ndb.StringProperty(required=True, indexed=False)
    picture = ndb.StringProperty(indexed=False)
    icon = ndb.StringProperty(indexed=False)
    sequence_number = ndb.IntegerProperty()

    @classmethod
    def get(cls, category_id):
        from models.config.config import config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.menu import get_category_by_id
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(int(category_id))
        elif app_kind == RESTO_APP:
            return get_category_by_id(category_id)

    @classmethod
    def get_initial_category(cls):
        category = cls.query(MenuCategory.category == None).get()
        if not category:
            category = cls(title=u'Начальная категория')
            category.put()
        return category

    def get_categories(self, venue=None):
        from models.config.config import config, AUTO_APP, RESTO_APP, DOUBLEB_APP
        from methods.proxy.resto.menu import get_categories as resto_get_categories
        from methods.proxy.doubleb.menu import get_categories as doubleb_get_categories
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            categories = MenuCategory.query(MenuCategory.category == self.key).fetch()
            if venue:
                for category in categories[:]:
                    if not category.get_items(venue=venue) and category.get_items():
                        categories.remove(category)
            return categories
        elif app_kind == RESTO_APP:
            return resto_get_categories(self)
        elif app_kind == DOUBLEB_APP:
            return doubleb_get_categories(self)

    def get_items(self, city=None, city_venues=None, only_available=False, venue=None):
        from methods.proxy.resto.menu import get_products as resto_get_products
        from methods.proxy.doubleb.menu import get_items as doubleb_get_products
        from models.config.config import config, AUTO_APP, RESTO_APP, DOUBLEB_APP
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            items = MenuItem.query(MenuItem.category == self.key).fetch()
        elif app_kind == RESTO_APP:
            items = resto_get_products(self)
        elif app_kind == DOUBLEB_APP:
            items = doubleb_get_products(self)
        else:
            items = []
        if only_available or city:
            for item in items[:]:
                if only_available and item.status != STATUS_AVAILABLE:
                    items.remove(item)
                    continue
                if city and len(item.restrictions) >= len(city_venues):
                    forbid = True
                    for venue_key in city_venues:
                        if venue_key not in item.restrictions:
                            forbid = False
                    if forbid:
                        items.remove(item)
                        continue
        if venue:
            for item in items[:]:
                if venue.key in item.restrictions:
                    items.remove(item)
        return items

    @staticmethod
    def generate_category_sequence_number():
        fastcounter.incr("category", delta=100, update_interval=1)
        return fastcounter.get_count("category") + random.randint(1, 100)

    def get_categories_in_order(self):
        return sorted(self.get_categories(), key=lambda category: category.sequence_number)

    def get_previous_category(self):
        parent = self.category.get()
        categories = parent.get_categories_in_order()
        index = categories.index(self)
        if index == 0:
            return None
        else:
            return categories[index - 1]

    def get_next_category(self):
        parent = self.category.get()
        categories = parent.get_categories_in_order()
        index = categories.index(self)
        if index == len(categories) - 1:
            return None
        else:
            return categories[index + 1]

    def generate_sequence_number(self):
        fastcounter.incr("category_%s" % self.key.id(), delta=100, update_interval=1)
        return fastcounter.get_count("category_%s" % self.key.id()) + random.randint(1, 100)

    def get_items_in_order(self, venue=None):
        return sorted(self.get_items(venue=venue), key=lambda item: item.sequence_number)

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

    def dict(self, venue=None, city=None, city_venues=None, exclude_items=False):
        subcategories = self.get_categories()
        items = []
        if not subcategories and not exclude_items:
            for item in self.get_items(city=city, city_venues=city_venues, only_available=True):
                if not venue:
                    items.append(item.dict())
                else:
                    if venue.key not in item.restrictions:
                        items.append(item.dict(venue=venue, without_restrictions=True))
        dct = {
            'info': {
                'category_id': str(self.key.id()),
                'title': self.title,
                'pic': self.picture,
                'restrictions': {
                    'venues': []  # todo: update restrictions logic for categories
                },
                'order': self.sequence_number if self.sequence_number else 0,
                'items_were_excluded': exclude_items
            },
            'items': items,
            'categories': [category.dict(venue, exclude_items=exclude_items) for category in subcategories]
        }
        if venue:
            del dct['info']['restrictions']
        return dct

    @classmethod
    def get_menu_dict(cls, venue=None, city=None, subscription_include=False, menu_frame_include=False):
        from models import Venue
        from methods.subscription import get_subscription_category_dict
        from models.config.menu import MenuFrameModule
        init_category = cls.get_initial_category()
        category_dicts = []
        if city:
            venue_keys = [city_venue.key for city_venue in Venue.get_suitable_venues(city)]
        else:
            venue_keys = []
        if menu_frame_include:
            exclude_items = MenuFrameModule.has_module()
        else:
            exclude_items = False
        for category in init_category.get_categories():
            category_dict = category.dict(venue=venue, city=city, city_venues=venue_keys, exclude_items=exclude_items)
            if category_dict['items'] or category_dict['categories'] or exclude_items:
                category_dicts.append(category_dict)
        if subscription_include:
            success, category_dict = get_subscription_category_dict()
            if success:
                logging.info('subscription is included')
                category_dicts.append(category_dict)
        return category_dicts


class PictureResizeMode(object):
    CENTER_CROP = 0
    CENTER_SHRINK = 1
    CHOICES = (CENTER_CROP, CENTER_SHRINK)


class MenuItem(PriceBase):
    category = ndb.KeyProperty(kind=MenuCategory)
    title = ndb.StringProperty(required=True)
    description = ndb.StringProperty(indexed=False)

    picture = ndb.StringProperty(indexed=False)  # source
    cut_picture = ndb.StringProperty(indexed=False)
    picture_resize_mode = ndb.IntegerProperty(choices=PictureResizeMode.CHOICES, default=PictureResizeMode.CENTER_CROP,
                                              indexed=False)
    picture_background = ndb.StringProperty(default="FFFFFF", indexed=False)

    icon = ndb.StringProperty(indexed=False)
    kal = ndb.IntegerProperty(indexed=False)
    weight = ndb.FloatProperty(indexed=False, default=0)
    volume = ndb.FloatProperty(indexed=False, default=0)

    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    sequence_number = ndb.IntegerProperty(default=0)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_modifiers = ndb.KeyProperty(kind=GroupModifier, repeated=True)

    restrictions = ndb.KeyProperty(repeated=True)  # kind=Venue (permanent use)
    time_restriction = ndb.IntegerProperty()  # min time in minutes
    group_choice_restrictions = ndb.IntegerProperty(repeated=True)  # GroupModifierChoice.choice_id
    stop_list_group_choices = ndb.IntegerProperty(repeated=True)    # GroupModifierChoice.choice_id

    rating = ndb.FloatProperty(default=0)  # in [0,1]

    @classmethod
    def get(cls, product_id):
        from models.config.config import config, AUTO_APP, RESTO_APP, DOUBLEB_APP
        from methods.proxy.resto.menu import get_product_by_id as resto_get_product_by_id
        from methods.proxy.doubleb.menu import get_product_by_id as doubleb_get_product_by_id
        app_kind = config.APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(int(product_id))
        elif app_kind == RESTO_APP:
            return resto_get_product_by_id(product_id)
        elif app_kind == DOUBLEB_APP:
            return doubleb_get_product_by_id(int(product_id))

    def dict(self, venue=None, without_restrictions=False):
        dct = {
            'id': str(self.key.id()),
            'order': self.sequence_number,
            'title': self.title,
            'description': self.description,
            'price': self.float_price_for_venue(venue.key.id()) if venue else self.float_price,
            'kal': self.kal,
            'pic': self.picture if not self.cut_picture else self.cut_picture,
            'pic_resize': self.picture_resize_mode,
            'pic_background': self.picture_background,
            'icon': self.icon,
            'weight': self.weight,
            'volume': self.volume,
            'single_modifiers': [SingleModifier.get(modifier.id()).dict(venue) for modifier in self.single_modifiers],
            'group_modifiers': [GroupModifier.get(modifier.id()).dict(self, venue) for modifier in self.group_modifiers],
            'restrictions': {
                'venues': [str(restrict.id()) for restrict in self.restrictions]
            }
        }
        if without_restrictions:
            del dct['restrictions']
        if not venue:
            dct['prices'] = self.venue_price_dicts
        return dct
