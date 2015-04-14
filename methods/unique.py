__author__ = 'dvpermyakov'


def unique(seq):
    if not seq:
        return []
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]