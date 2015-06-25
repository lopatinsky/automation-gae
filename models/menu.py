# coding=utf-8
import random
from google.appengine.ext import ndb
from methods import fastcounter
from models import STATUS_AVAILABLE, STATUS_UNAVAILABLE

SINGLE_MODIFIER = 0
GROUP_MODIFIER = 1


class SingleModifier(ndb.Model):
    INFINITY = 1000

    title = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(default=0)  # в копейках
    min_amount = ndb.IntegerProperty(default=0)
    max_amount = ndb.IntegerProperty(default=0)

    @property
    def float_price(self):  # в рублях
        return float(self.price) / 100.0

    def dict(self):
        return {
            'modifier_id': str(self.key.id()),
            'title': self.title,
            'price': float(self.price) / 100.0,  # в рублях
            'min': self.min_amount,
            'max': self.max_amount
        }


class GroupModifierChoice(ndb.Model):
    choice_id = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(default=0)  # в копейках
    default = ndb.BooleanProperty(default=False)

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

    def get_choice_by_id(self, choice_id):
        for choice in self.choices:
            if choice_id == choice.choice_id:
                return choice
        return None

    @classmethod
    def get_modifier_by_choice(cls, choice_id):
        for modifier in cls.query().fetch():
            for choice in modifier.choices:
                if choice.choice_id == choice_id:
                    return modifier
        return None

    def dict(self, product=None):
        choices = [choice for choice in self.choices
                   if product is None or choice.choice_id not in product.group_choice_restrictions]
        return {
            'modifier_id': str(self.key.id()),
            'title': self.title,
            'choices': [
                {
                    'default': choice.default,
                    'title': choice.title,
                    'price': float(choice.price) / 100.0,  # в рублях
                    'id': str(choice.choice_id)
                } for choice in choices
            ]
        }


class MenuItem(ndb.Model):
    title = ndb.StringProperty(required=True)
    description = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=False)  # source
    cut_picture = ndb.StringProperty(indexed=False)
    icon = ndb.StringProperty(indexed=False)
    kal = ndb.IntegerProperty(indexed=False)
    weight = ndb.FloatProperty(indexed=False, default=0)
    volume = ndb.FloatProperty(indexed=False, default=0)
    price = ndb.IntegerProperty(default=0, indexed=False)  # в копейках

    status = ndb.IntegerProperty(required=True, choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE),
                                 default=STATUS_AVAILABLE)
    sequence_number = ndb.IntegerProperty(default=0)
    single_modifiers = ndb.KeyProperty(kind=SingleModifier, repeated=True)
    group_modifiers = ndb.KeyProperty(kind=GroupModifier, repeated=True)

    restrictions = ndb.KeyProperty(repeated=True)  # kind=Venue (permanent use)
    group_choice_restrictions = ndb.IntegerProperty(repeated=True)  # GroupModifierChoice.choice_id
    stop_list_group_choices = ndb.IntegerProperty(repeated=True)    # GroupModifierChoice.choice_id

    @property
    def float_price(self):  # в рублях
        return float(self.price) / 100.0

    def get_category(self):
        from models import MenuCategory
        for category in MenuCategory.query().fetch():
            if self.key in category.menu_items:
                return category

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
            'single_modifiers': [modifier.get().dict() for modifier in self.single_modifiers],
            'group_modifiers': [modifier.get().dict(self) for modifier in self.group_modifiers],
            'restrictions': {
                'venues': [str(restrict.id()) for restrict in self.restrictions]
            }
        }
        if without_restrictions:
            del dct['restrictions']
        return dct


class MenuCategory(ndb.Model):
    title = ndb.StringProperty(required=True, indexed=False)
    picture = ndb.StringProperty(indexed=False)
    menu_items = ndb.KeyProperty(kind=MenuItem, repeated=True, indexed=False)
    status = ndb.IntegerProperty(choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE), default=STATUS_AVAILABLE)
    sequence_number = ndb.IntegerProperty()

    restrictions = ndb.KeyProperty(repeated=True)  # kind=Venue not implemented

    @staticmethod
    def generate_category_sequence_number():
        fastcounter.incr("category", delta=100, update_interval=1)
        return fastcounter.get_count("category") + random.randint(1, 100)

    @staticmethod
    def get_categories_in_order():
        return sorted([category for category in MenuCategory.query().fetch()],
                      key=lambda category: category.sequence_number)

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
        return sorted([item.get() for item in self.menu_items], key=lambda item: item.sequence_number)

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
        for item in self.menu_items:
            item = item.get()
            if item.status != STATUS_AVAILABLE:
                continue
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
                    'venues': [str(restrict.id()) for restrict in self.restrictions]
                },
                'order': self.sequence_number if self.sequence_number else 0
            },
            'items': items
        }
        if venue:
            del dct['info']['restrictions']
        return dct
