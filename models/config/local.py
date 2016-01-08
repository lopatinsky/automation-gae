import threading

from google.appengine.api import namespace_manager

__author__ = 'dvpermyakov'


class LocalConfigProxy(object):
    _local = threading.local()

    def __init__(self):
        self._local.config = None

    @property
    def _config_object(self):
        from models.config.config import Config
        if self._local.config:
            if self._local.config.key.namespace() == namespace_manager.get_namespace():
                return self._local.config
        self._local.config = Config.get()
        return self._local.config

    def __getattr__(self, item):
        return getattr(self._config_object, item)

    def __nonzero__(self):
        return bool(self._config_object)
