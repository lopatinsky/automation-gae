def get_item_keys(item_dicts):
    result = {}
    for item_dict in item_dicts:
        if result.get(item_dict['item'].key):
            result[item_dict['item'].key].append(item_dict)
        else:
            result[item_dict['item'].key] = [item_dict]
    return result


def set_discounts(outcome, item_dicts, promo):
    def apply_discounts(item_dict):
        if promo not in item_dict['promos']:
            if item_dict['revenue'] >= item_dict['price'] * discount:
                item_dict['revenue'] -= item_dict['price'] * discount
                item_dict['promos'].append(promo)
                return True
        return False

    discount = float(outcome.value) / 100.0
    item_keys = get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item):
        for item_dict in item_keys[outcome.item]:
            if apply_discounts(item_dict):
                promo_applied = True
    if not outcome.item_required:
        for item_dict in item_dicts:
            if apply_discounts(item_dict):
                promo_applied = True
    return promo_applied