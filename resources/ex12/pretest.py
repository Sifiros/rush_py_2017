#!/usr/bin/env python3

import sys

with open(sys.argv[1], "r") as f:
    content = f.read()
if "system" in content:
    sys.stderr.write("system used\n")
