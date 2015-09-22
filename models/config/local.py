import threading

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
        return self._local.config

    def __getattr__(self, item):
        return getattr(self._config_object, item)
