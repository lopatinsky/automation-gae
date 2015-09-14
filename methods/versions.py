from datetime import datetime

from models.config.config import Config, Version, TEST_VERSIONS

__author__ = 'dvpermyakov'


def is_test_version(url):
    test = False
    for version in TEST_VERSIONS:
        if version in url:
            test = True
    return test


def get_version(version):
    version = int(version)
    config = Config.get()
    for version_obj in config.VERSIONS:
        if version_obj.number == version:
            return version_obj
    now = datetime.utcnow()
    version_obj = Version(created=now, updated=now, number=version)
    config.VERSIONS.append(version_obj)
    config.put()
    return version_obj


def is_available_version(version):
    version = int(version)
    version_obj = get_version(version)
    return version_obj.available


def update_company_versions(version):
    version = int(version)
    config = Config.get()
    version_obj = get_version(version)
    version_obj.updated = datetime.utcnow()
    config.put()
