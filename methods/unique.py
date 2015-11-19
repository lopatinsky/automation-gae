__author__ = 'dvpermyakov'

USER_AGENT = 0
VERSION = 1

temporary_user = {
    USER_AGENT: 'initial',
    VERSION: 0
}


def unique(seq):
    if not seq:
        return []
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def set_user_agent(user_agent):
    temporary_user[USER_AGENT] = user_agent


def set_user_version(version):
    temporary_user[VERSION] = version


def get_temporary_user():
    return temporary_user
