#!/usr/bin/env python3

def FakeClass(cls):
    def p(name):
        return lambda *args, **kw: print(f"{cls.__name__}.{name} {args[1:]} {kw}")
    for name, attr in cls.__dict__.items():
        if callable(attr):
            setattr(cls, name, p(name))
    return cls

def Verbosable(cls):
    default = False
    def verbose_get(self):
        return self.__verbose
    def verbose_set(self, v):
        self.__verbose = not not v
    verbose = property(verbose_get)
    verbose = verbose.setter(verbose_set)
    if hasattr(cls, "__init__"):
        init = getattr(cls, "__init__")
        def __init__(self, *args, **kw):
            self.verbose = kw.get("verbose", default)
            kw.pop("verbose", None)
            init(self, *args, **kw)
    else:
        def __init__(self, verbose=default):
            self.verbose = verbose
    def vprint(self, *args, **kw):
        if self.verbose:
            print(*args, **kw)
    setattr(cls, "__init__", __init__)
    setattr(cls, "verbose", verbose)
    setattr(cls, "vprint", vprint)
    return cls
