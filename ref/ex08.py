#!/usr/bin/env python3

import os
import sys

for i, path in enumerate(sys.argv[1:] if len(sys.argv) > 1 else ["."]):
    print("\n" * (not not i), end="")
    orig = len(path.strip('/').split('/'))
    for d, sd, fs in os.walk(path):
        ds = d.strip('/').split('/')
        diff = len(ds) - orig
        print((diff != 0) * "|" + (diff - 1) * "  |" + (diff != 0) * "--" + ds[-1])
