import threading

from google.appengine.api import namespace_manager

__author__ = 'dvpermyakov'


class LocalConfigProxy(object):
    _local = threading.local()

    @property
    def _config_object(self):
        from models.config.config import Config

        try:
            self._local.config
        except AttributeError:
            self._local.config = Config.get()
        else:
            if not self._local.config or self._local.config.key.namespace != namespace_manager.get_namespace():
                self._local.config = Config.get()

        return self._local.config

    def __getattr__(self, item):
        return getattr(self._config_object, item)

    def __nonzero__(self):
        return bool(self._config_object)
