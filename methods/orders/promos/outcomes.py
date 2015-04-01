def get_item_keys(item_dicts):
    result = {}
    for item_dict in item_dicts:
        result[item_dict['item'].key] = item_dict
    return result


def set_discounts(outcome, item_dicts, promo_id):
    discount = outcome.value / 100
    item_keys = get_item_keys(item_dicts)
    if item_keys.get(outcome.item):
        item_dict = item_keys[outcome.item]
        if item_dict['revenue'] >= item_dict['price'] * discount:
            item_dict['revenue'] -= item_dict['price'] * discount
            item_dict['promos'].append(promo_id)
            return True
    return False