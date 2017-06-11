from collections import defaultdict


class Statics(object):
    RESOLVED_IMPORTS = {}
    CODE_BY_MODULE = defaultdict(list)
