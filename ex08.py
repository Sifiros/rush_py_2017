#!/usr/bin/python3

import os
import sys

for path in sys.argv[1:] if len(sys.argv) > 1 else ["."]:
    orig = len(path.strip('/').split('/'))
    for d, sd, fs in os.walk(path):
        ds = d.strip('/').split('/')
        diff = len(ds) - orig
        print((diff != 0) * "|" + (diff - 1) * "  |" + (diff != 0) * "--" + ds[-1])
