import os
from google.appengine.api.namespace_manager import namespace_manager


def namespace_manager_default_namespace_for_request():
    if len(os.environ['SERVER_NAME'].split('.')) < 5:
        return namespace_manager.google_apps_namespace()
    else:
        return os.environ['SERVER_NAME'].split('.')[0]