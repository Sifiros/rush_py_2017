#!/usr/bin/env python3

import json

class Json(object):
    class Internal:
        def __init__(self, d):
            self._keys = sorted(list(d.keys()))
            self.__dict__.update({ k: Json(v) for k, v in d.items()})
        def __str__(self):
            return str(self.__dict__)
        def __repr__(self):
            return repr(self.__dict__)
        def __contains__(self, key):
            return key in self._keys
        def get(self, value, default=None):
            return self.__dict__[value] if value in self else default
        def iteritems(self):
            for key in self._keys:
                yield key, self.__dict__[key]
    def __new__(cls, o):
        if type(o) is list:
            return [Json(e) for e in o]
        if type(o) is dict:
            return Json.Internal(o)
        return o

def load(path):
    with open(path, "r") as f:
        return Json(json.load(f))
