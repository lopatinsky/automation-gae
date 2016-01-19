from datetime import datetime
import logging

from google.appengine.api.namespace_manager import namespace_manager
from models.config.version import TEST_VERSIONS, Version, CURRENT_VERSION, CURRENT_APP_ID, PRODUCTION_APP_ID, \
    DEMO_APP_ID
from models.config.config import Config, config
from models.proxy.unified_app import AutomationCompany

__author__ = 'dvpermyakov'

CLIENT_VERSIONS = {
    0: 'farsh/1.1.1.3',
    1: 'Pastadeli/1.1.4',
    2: 'Pastadeli/1.1.3',
    3: 'Magnolia/1.0',
    4: 'SushiCrab/1.0',
    5: 'Ladolchevita/1.0',
    6: 'MeatMe/1.1.2',
    7: 'Chikarabar/1.0.2',
    8: 'Banzay/1.0',
    9: '7 Donuts/1.0'
}


def is_test_version():
    return CURRENT_VERSION in TEST_VERSIONS


def get_version(version, create=False):
    version = int(version)
    version_obj = None
    cfg = Config.get()
    for version_obj in cfg.VERSIONS:
        if version_obj.number == version:
            return version_obj
    if create:
        now = datetime.utcnow()
        version_obj = Version(created=now, updated=now, number=version)
        cfg.VERSIONS.append(version_obj)
        cfg.put()
    return version_obj


def is_available_version(version):
    version = int(version)
    version_obj = get_version(version)
    return version_obj is None or version_obj.available


def update_company_versions(version):
    version = int(version)
    version_obj = get_version(version, create=True)
    version_obj.updated = datetime.utcnow()
    version_obj.put()


def update_namespace(namespace):
    init_namespace = None

    if CURRENT_APP_ID == PRODUCTION_APP_ID:
        if not config:
            logging.debug('namespace=%s' % namespace_manager.get_namespace())
            return False, init_namespace
        logging.debug('initial namespace=%s' % namespace_manager.get_namespace())
        if namespace:
            proxy_company = AutomationCompany.query(AutomationCompany.namespace == namespace).get()
            if proxy_company:
                init_namespace = namespace_manager.get_namespace()
                namespace_manager.set_namespace(namespace)
    elif CURRENT_APP_ID == DEMO_APP_ID:
        if not namespace_manager.get_namespace():
            namespace_manager.set_namespace(namespace)

    logging.debug('namespace=%s' % namespace_manager.get_namespace())
    return True, init_namespace
