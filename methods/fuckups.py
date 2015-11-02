import logging
from google.appengine.api.namespace_manager import namespace_manager
from methods.emails import admins
from models.venue import DELIVERY, SELF, IN_CAFE

__author__ = 'dvpermyakov'


def fuckup_redirection_namespace():
    if namespace_manager.get_namespace() == 'mycompany':
        namespace_manager.set_namespace('shashlichniydom')
    if namespace_manager.get_namespace() == 'mycompany2':
        namespace_manager.set_namespace('mycompany')


# 13.10.2015
def fuckup_ios_delivery_types(user_agent, version, delivery_types):
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
    if 'iOS' not in user_agent or version != '2' or RESTRICTION.get(namespace_manager.get_namespace()) == None:
        return delivery_types
    send_error = False
    for delivery_type in delivery_types[:]:
        if int(delivery_type['id']) in RESTRICTION.get(namespace_manager.get_namespace()):
            delivery_types.remove(delivery_type)
            send_error = True
    if send_error:
        logging.warning('Cut delivery types: %s' % delivery_types)
        admins.send_error('ios_fuckup', 'Catch Version 2 with 2 delivery types', str({
            'user_agent': user_agent,
            'delivery_types': delivery_types,
            'version': version,
            'namespace': namespace_manager.get_namespace()
        }))
    return delivery_types
