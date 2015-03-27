# coding=utf-8
import logging
from models import OrderPositionDetails, ChosenGroupModifierDetails


def _nice_join(strs):
    if not strs:
        return ""
    if len(strs) == 1:
        return strs[0]
    return u"%s и %s" % (", ".join(strs[:-1]), strs[-1])


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


def _unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def _group_item_dicts(item_dicts):
    result = []
    for item_dict in item_dicts:
        possible_group = result[-1] if result else {'id': None}
        if item_dict['item'].key.id() == possible_group['id']:
            possible_group['quantity'] += 1
            possible_group['promos'].extend(item_dict['promos'])
            possible_group['errors'].extend(item_dict['errors'])
        else:
            result.append({
                'id': item_dict['item'].key.id(),
                'promos': item_dict['promos'],
                'errors': item_dict['errors'],
                'quantity': 1
            })
    for dct in result:
        dct['promos'] = _unique(dct['promos'])
        dct['errors'] = _unique(dct['errors'])
    return result


def validate_order(client, items, payment_info, venue, delivery_time, with_details=False):
    item_dicts = []
    for item in items:
        price = item.price
        for single_modifier in item.chosen_single_modifiers:
            price += single_modifier.price
        for group_modifier in item.chosen_group_modifiers:
            price += group_modifier.choice.price
        item_dicts.append({
            'item': item,
            'single_modifiers': item.chosen_single_modifiers,
            'group_modifiers': item.chosen_group_modifiers,
            'price': price,
            'revenue': price,
            'errors': [],
            'promos': []
        })

    errors = []
    valid = True
    promos_info = []

    valid = _check_venue(venue, delivery_time, errors) and valid

    total_sum = 0
    for item_dict in item_dicts:
        total_sum += item_dict['price']

    grouped_item_dicts = _group_item_dicts(item_dicts)

    result = {
        'valid': valid,
        'errors': errors,
        'items': grouped_item_dicts,
        'promos': promos_info,
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
                promos=item_dict['promos'],
                single_modifiers=[modifier.key for modifier in item_dict['single_modifiers']],
                group_modifiers=[ChosenGroupModifierDetails(chosen_group_modifier_name=modifier.choice,
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
