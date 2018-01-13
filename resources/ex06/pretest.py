#!/usr/bin/env python3

import sys

with open(sys.argv[1], "r") as f:
    content = f.read()
for kw in ["while", "for"]:
    if kw in content:
        sys.stderr.write(f"{kw} used\n")
        exit(0)
