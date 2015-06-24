# coding=utf-8
from config import config
from methods.map import get_streets_by_address, get_houses_by_address

__author__ = 'dvpermyakov'


def check_address(address):
    address = address['address']
    if not address:
        return False, u'Введите адрес'
    if not address['city']:
        return False, u'Не выбран город'
    if not address['street']:
        return False, u'Не Выбрана улица'
    if config.COMPULSORY_ADDRESS_VALIDATES:
        street_found = False
        candidates = get_streets_by_address(address['city'], address['street'])
        for candidate in candidates:
            if candidate['address']['city'] == address['city']:
                if candidate['address']['street'] == address['street']:
                    street_found = True
        if not street_found:
            error = u'Введенная улица не найдена'
            if address['home']:
                if candidates:
                    error += u'. Возможно, Вы имели ввиду улицу "%s"' % candidates[0]['address']['street']
                return False, error
            else:
                return False, u'. Возможно, Вы пропустили разграничитель между улицей и домом - запятую'
        else:
            if not address['home']:
                return False, u'Введите номер дома'
        home_found = False
        candidates = get_houses_by_address(address['city'], address['street'], address['home'])
        for candidate in candidates:
            if candidate['address']['city'] == address['city']:
                if candidate['address']['street'] == address['street']:
                    if candidate['address']['home'] == address['home']:
                        home_found = True
        if not home_found:
            return False, u'Введенный дом не найден'
    if not address['flat']:
        return False, u'Не выбрана квартира'
    return True, None