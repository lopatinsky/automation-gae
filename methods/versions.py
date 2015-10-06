from datetime import datetime

from models.config.config import Config
from models.config.version import TEST_VERSIONS, Version

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


def is_test_version(url):
    test = False
    for version in TEST_VERSIONS:
        if version in url:
            test = True
    return test


def get_version(version, create=False):
    version = int(version)
    version_obj = None
    config = Config.get()
    for version_obj in config.VERSIONS:
        if version_obj.number == version:
            return version_obj
    if create:
        now = datetime.utcnow()
        version_obj = Version(created=now, updated=now, number=version)
        config.VERSIONS.append(version_obj)
        config.put()
    return version_obj


def is_available_version(version):
    version = int(version)
    version_obj = get_version(version)
    return version_obj and version_obj.available


def update_company_versions(version):
    version = int(version)
    version_obj = get_version(version, create=True)
    version_obj.updated = datetime.utcnow()
    version_obj.put()
