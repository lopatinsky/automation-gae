# coding=utf-8
import logging
from google.appengine.ext import ndb
from models import OrderPositionDetails, ChosenGroupModifierDetails, MenuItem, SingleModifier, GroupModifier
from promos import apply_promos


def _nice_join(strs):
    if not strs:
        return ""
    if len(strs) == 1:
        return strs[0]
    return u"%s и %s" % (", ".join(strs[:-1]), strs[-1])


def _check_modifier_consistency(item_dicts, errors):
    description = None
    for item_dict in item_dicts:
        item = item_dict['item']
        for single_modifier in item.chosen_single_modifiers:
            if single_modifier.key not in item.single_modifiers:
                description = u'%s нет для %s' % (single_modifier.title, item.title)
                errors.append(description)
                item_dict['errors'].append(description)
        for group_modifier in item.chosen_group_modifiers:
            if group_modifier.key not in item.group_modifiers:
                description = u'%s нет для %s' % (group_modifier.title, item.title)
                errors.append(description)
                item_dict['errors'].append(description)
            choice_confirmed = False
            for choice in group_modifier.choices:
                if choice.title == group_modifier.choice.title:
                    choice_confirmed = True
            if not choice_confirmed:
                description = u'%s нет для %s' % (group_modifier.choice.title, group_modifier.title)
                errors.append(description)
                item_dict['errors'].append(description)
    if description:
        return False
    else:
        return True


def _check_venue(venue, delivery_time, errors):
    if venue:
        if not venue.active:
            logging.warn("order attempt to inactive venue: %s", venue.key.id())
            errors.append(u"Эта кофейня сейчас недоступна")
            return False
        if not venue.is_open(minutes_offset=delivery_time):
            errors.append(u"Эта кофейня сейчас закрыта")
            return False
        if venue.problem:
            errors.append(u"Кофейня временно не принимает заказы: %s" % venue.problem)
            return False
    return True


def _check_restrictions(venue, item_dicts, errors):
    description = None
    for item_dict in item_dicts:
        item = item_dict['item']
        if venue.key in item.restrictions:
            description = u'%s не имеет %s' % (venue.title, item.title)
            errors.append(description)
            item_dict['errors'].append(description)
    if description:
        return False
    else:
        return True


def _check_stop_list(venue, item_dicts, errors):
    description = None
    for item_dict in item_dicts:
        item = item_dict['item']
        if item.key in venue.stop_lists:
            description = u'%s положил %s в стоп лист' % (venue.title, item.title)
            errors.append(description)
            item_dict['errors'].append(description)
    if description:
        return False
    else:
        return True


def _unique(seq):
    if not seq:
        return []
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def _group_promos(promos):
    if not promos:
        return []
    result = {}
    for promo in promos:
        if promo.key.id() not in result:
            result[promo.key.id()] = promo
    return [promo.validation_dict() for promo in result.values()]


def _is_equal(item_dict1, item_dict2):
    if not item_dict1 or not item_dict2:
        return False
    if item_dict1['item'].key != item_dict2['item'].key:
        return False
    if len(item_dict1['single_modifier_keys']) != len(item_dict2['single_modifier_keys']):
        return False
    for i in xrange(len(item_dict1['single_modifier_keys'])):
        if item_dict1['single_modifier_keys'][i] != item_dict2['single_modifier_keys'][i]:
            return False
    for i in xrange(len(item_dict1['group_modifier_keys'])):
        if item_dict1['group_modifier_keys'][i][0] != item_dict2['group_modifier_keys'][i][0]:
            return False
        if item_dict1['group_modifier_keys'][i][1] != item_dict2['group_modifier_keys'][i][1]:
            return False
    return True


def _group_single_modifiers(modifiers):
    result = {}
    for modifier in modifiers:
        if modifier.id() in result:
            result[modifier.id()]['quantity'] += 1
        else:
            result[modifier.id()] = {
                'id': str(modifier.id()),
                'quantity': 1
            }
    return result.values()


def _group_group_modifiers(modifiers):
    result = {}
    for modifier in modifiers:
        key = '%s%s' % (modifier[0].id, modifier[1])
        if key in result:
            result[key]['quantity'] += 1
        else:
            result[key] = {
                'id': str(modifier[0].id()),
                'choice': str(modifier[1]),
                'quantity': 1
            }
    return result.values()


def group_item_dicts(item_dicts):
    result = []
    for item_dict in item_dicts:
        possible_group = result[-1] if result else {'id': None}
        if _is_equal(item_dict, possible_group.get('item_dict')):
            possible_group['quantity'] += 1
            if item_dict.get('promos'):
                possible_group['promos'].extend(item_dict.get('promos'))
            if item_dict.get('errors'):
                possible_group['errors'].extend(item_dict['errors'])
        else:
            if possible_group.get('item_dict'):
                del possible_group['item_dict']
            result.append({
                'id': str(item_dict['item'].key.id()),
                'title': item_dict['item'].title,
                'promos': item_dict.get('promos'),
                'errors': item_dict.get('errors'),
                'quantity': 1,
                'price_without_promos': item_dict['price'],
                'single_modifiers': _group_single_modifiers(item_dict['single_modifier_keys']),
                'group_modifiers': _group_group_modifiers(item_dict['group_modifier_keys']),
                'item_dict': item_dict
            })
    if result[-1].get('item_dict'):
            del result[-1]['item_dict']
    for dct in result:
        dct['promos'] = _group_promos(dct.get('promos'))
        dct['errors'] = _unique(dct.get('errors'))
    return result


def set_modifiers(items):
    mod_items = []
    for item in items:
        menu_item = MenuItem.get_by_id(int(item['item_id']))
        menu_item.chosen_single_modifiers = []
        for single_modifier in item['single_modifiers']:
            single_modifier_obj = SingleModifier.get_by_id(int(single_modifier['single_modifier_id']))
            for i in xrange(single_modifier['quantity']):
                menu_item.chosen_single_modifiers.append(single_modifier_obj)
        menu_item.chosen_group_modifiers = []
        for group_modifier in item['group_modifiers']:
            group_modifier_obj = GroupModifier.get_by_id(int(group_modifier['group_modifier_id']))
            group_modifier_obj.choice = group_modifier_obj.get_choice_by_id(int(group_modifier['choice']))
            if group_modifier_obj.choice:
                for i in xrange(group_modifier['quantity']):
                    menu_item.chosen_group_modifiers.append(group_modifier_obj)
        for i in xrange(item['quantity']):
            mod_items.append(menu_item)
    return mod_items


def set_price_with_modifiers(items):
    for item in items:
        price = item.price
        for single_modifier in item.chosen_single_modifiers:
            price += single_modifier.price
        for group_modifier in item.chosen_group_modifiers:
            price += group_modifier.choice.price
        item.total_price = price
    return items


def validate_order(client, items, payment_info, venue, delivery_time, delivery_type, with_details=False):
    items = set_modifiers(items)
    items = set_price_with_modifiers(items)

    item_dicts = []
    for item in items:
        item_dicts.append({
            'item': item,
            'single_modifiers': item.chosen_single_modifiers,
            'group_modifiers': item.chosen_group_modifiers,
            'single_modifier_keys': [modifier.key for modifier in item.chosen_single_modifiers],
            'group_modifier_keys': [(modifier.key, modifier.choice.choice_id)
                                    for modifier in item.chosen_group_modifiers],
            'price': item.total_price,
            'revenue': item.total_price,
            'errors': [],
            'promos': []
        })

    errors = []
    valid = True
    valid = _check_venue(venue, delivery_time, errors) and valid
    valid = _check_modifier_consistency(item_dicts, errors) and valid
    valid = _check_restrictions(venue, item_dicts, errors) and valid
    valid = _check_stop_list(venue, item_dicts, errors) and valid

    item_dicts, promos_info = apply_promos(venue, client, item_dicts, payment_info, delivery_time, delivery_type)

    total_sum = 0
    for item_dict in item_dicts:
        total_sum += item_dict['revenue']

    logging.info(item_dicts)

    grouped_item_dicts = group_item_dicts(item_dicts)

    result = {
        'valid': valid,
        'errors': errors,
        'items': grouped_item_dicts,
        'promos': [promo.validation_dict() for promo in promos_info],
        'total_sum': total_sum
    }
    logging.info(result)

    if with_details:
        details = []
        for item_dict in item_dicts:
            details_item = OrderPositionDetails(
                item=item_dict['item'].key,
                price=item_dict['price'],
                revenue=item_dict['revenue'],
                promos=[promo.key for promo in item_dict['promos']],
                single_modifiers=[modifier.key for modifier in item_dict['single_modifiers']],
                group_modifiers=[ChosenGroupModifierDetails(group_choice_id=modifier.choice.choice_id,
                                                            group_modifier=modifier.key)
                                 for modifier in item_dict['group_modifiers']]
            )
            details_item.errors = item_dict['errors']
            details.append(details_item)
        result['details'] = details

    return result


def get_first_error(validation_result):
    if validation_result['errors']:
        return validation_result['errors'][0]
    for item in validation_result['details']:
        if item.errors:
            return item.errors[0]
    return None
