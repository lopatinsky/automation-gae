import logging
from google.appengine.api.namespace_manager import namespace_manager
from methods.emails import admins
from methods.unique import get_temporary_user, USER_AGENT, VERSION, is_ios_user, is_android_user
from models.venue import DELIVERY, SELF, IN_CAFE

__author__ = 'dvpermyakov'


# 13.10.2015
def fuckup_ios_delivery_types(delivery_types):
    RESTRICTION = {
        'meatme': [DELIVERY],
        'sushimarket': [DELIVERY],
        'nasushi': [DELIVERY],
        'perchiniribaris': [SELF, IN_CAFE],
        'perchiniribarislublino': [SELF, IN_CAFE],
        'burgerhouse': [SELF, IN_CAFE],
        'tykano': [SELF, IN_CAFE],
        'magnolia': [SELF, IN_CAFE],
        'chikarabar': [SELF, IN_CAFE],
        'sushivesla': [DELIVERY],
        'pastadeli': [SELF, IN_CAFE]
    }
    user = get_temporary_user()
    if not is_ios_user() or user.get(VERSION) != 2 or RESTRICTION.get(namespace_manager.get_namespace()) == None:
        return delivery_types
    send_error = False
    for delivery_type in delivery_types[:]:
        if int(delivery_type['id']) in RESTRICTION.get(namespace_manager.get_namespace()):
            delivery_types.remove(delivery_type)
            send_error = True
    if send_error:
        logging.warning('Cut delivery types: %s' % delivery_types)
        admins.send_error('ios_fuckup', 'Catch Version 2 with 2 delivery types', str({
            'user_agent': user.get(USER_AGENT),
            'delivery_types': delivery_types,
            'version': user.get(VERSION),
            'namespace': namespace_manager.get_namespace()
        }))
    return delivery_types


# 25.11.2015
def is_share_fuckup_ios_user():
    user = get_temporary_user()
    is_elephant_ua = 'ElephantBoutique/1.1.8' in user.get(USER_AGENT)
    is_red_cup_ua = 'RedCup' in user.get(USER_AGENT)
    return is_ios_user() and user.get(VERSION) < 5 and not is_elephant_ua and not is_red_cup_ua


# old
def fuckup_order_channel(channel, order):
    IOS_FUCKUP = ['Pastadeli/1.0', 'Pastadeli/1.1', 'ElephantBoutique/1.0', 'MeatMe/1.0']
    ANDROID_FUCKUP = ['pastadeli/4', 'pastadeli/5', 'meatme/4', 'meatme/5']
    if is_android_user():
        for fuckup in ANDROID_FUCKUP:
            if fuckup in order.user_agent:
                channel = 'order_%s' % order.key.id()
    if is_ios_user():
        for fuckup in IOS_FUCKUP:
            if fuckup in order.user_agent:
                channel = 'order_%s' % order.key.id()
    return channel
