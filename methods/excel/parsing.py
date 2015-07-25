# coding=utf-8
import logging
from methods.excel import xlrd
from models import MenuCategory, MenuItem, GroupModifier, GroupModifierChoice

__author__ = 'dvpermyakov'


def menu_parse(file_excel):
    wb = xlrd.open_workbook(file_contents=file_excel)
    sh = wb.sheet_by_index(0)
    categories = {}
    products = {}
    group_modifiers = {}
    group_choices = {}
    for row_number in range(sh.nrows):
        if row_number > 0:
            current_category = MenuCategory()
            current_item = MenuItem()
            current_modifier = GroupModifier()
            current_choice = GroupModifierChoice()
            item_add = True
            for index, cell in enumerate(sh.row_values(row_number)):
                if index == 0:
                    current_category.sequence_number = int(cell)
                    current_item.sequence_number = int(cell)
                elif index == 1:
                    if categories.get(cell):
                        current_category = categories[cell]
                    else:
                        current_category.title = cell
                        categories[cell] = current_category
                elif index == 2:
                    if products.get(cell):
                        current_item = products[cell]
                        item_add = False
                    else:
                        current_item.title = cell
                        products[cell] = current_item
                elif index == 3:
                    if item_add:
                        current_item.description = cell
                elif index == 4 and cell:
                    if item_add:
                        current_item.price = int(float(cell) * 100)
                elif index == 5:
                    if item_add and cell:
                        current_item.volume = float(cell)
                elif index == 6:
                    if item_add and cell:
                        current_item.weight = float(cell)
                elif index == 7:
                    if item_add and cell:
                        current_item.kal = int(cell)
                elif index == 8:
                    if cell:
                        if group_modifiers.get(cell):
                            current_modifier = group_modifiers[cell]
                        else:
                            current_modifier.title = cell
                            group_modifiers[cell] = current_modifier
                elif index == 9:
                    if cell:
                        current_choice.title = cell
                elif index == 10:
                    if cell or cell == 0:
                        current_choice.price = int(float(cell) * 100)
                        key = '%s_%s' % (current_choice.title, current_choice.price)
                        if group_choices.get(key):
                            current_choice = group_choices[key]
                        else:
                            current_choice.choice_id = GroupModifierChoice.generate_id()
                            group_choices[key] = current_choice
                        if current_choice not in current_modifier.choices:
                            current_modifier.choices.append(current_choice)
                            current_choice.put()
            logging.info(current_modifier)
            if current_modifier.title:
                current_modifier.put()
                if current_modifier.key not in current_item.group_modifiers:
                    current_item.group_modifiers.append(current_modifier.key)
            current_item.put()
            if item_add:
                current_item.category = current_category.key
            current_category.put()