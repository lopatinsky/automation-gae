import webapp2

__author__ = 'dvpermyakov'

USER_AGENT = 0
VERSION = 1


def unique(seq):
    if not seq:
        return []
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def get_temporary_user():
    request = webapp2.get_request()
    return {
        USER_AGENT: request.headers['User-Agent'],
        VERSION: int(request.headers.get('Version') or 0),
    }


def is_ios_user():
    user = get_temporary_user()
    return 'iOS' in user.get(USER_AGENT)


def is_android_user():
    user = get_temporary_user()
    return 'Android' in user.get(USER_AGENT)
