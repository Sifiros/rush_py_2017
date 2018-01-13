#!/usr/bin/env python3

import sys

size = 42
with open(sys.argv[1], "r") as f:
    if len(f.read()) > size:
        sys.stderr.write("Program too long\n")
