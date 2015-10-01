import os


def namespace_manager_default_namespace_for_request():
    if len(os.environ['SERVER_NAME'].split('.')) < 5:
        return ''
    else:
        return os.environ['SERVER_NAME'].split('.')[0]
