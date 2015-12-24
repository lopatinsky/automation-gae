import os
from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

def namespace_manager_default_namespace_for_request():
    host_parts = os.environ['SERVER_NAME'].split('.')
    if host_parts[-1] == 'mobi' and host_parts[-2] == 'rbcn' and host_parts[-3] not in ('auto', 'demo'):
        return host_parts[-3]
    elif len(host_parts) == 5:
        return host_parts[0]
    else:
        return ''
