#!/usr/bin/env python3

import sys

count = 0
with open(sys.argv[1], "r") as f:
    for line in f.read().split("\n"):
        if ";" in line:
            sys.stderr.write("Usage of a ;\n")
            exit(0)
        if not line or line.startswith("#") or line.startswith("import") or line.startswith("from"):
            continue
        if count:
            sys.stderr.write("More than one line\n")
            exit(0)
        count = 1
