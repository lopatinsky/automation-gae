# parse_qs
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

# json
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json

# httplib2

# socks
try:
    from methods.sms.twilio.libs.httplib2 import socks
    from methods.sms.twilio.libs import (
        PROXY_TYPE_HTTP,
        PROXY_TYPE_SOCKS4,
        PROXY_TYPE_SOCKS5
    )
except ImportError:
    from methods.sms.twilio.libs import socks
    from methods.sms.twilio.libs import (
        PROXY_TYPE_HTTP,
        PROXY_TYPE_SOCKS4,
        PROXY_TYPE_SOCKS5
    )
