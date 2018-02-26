#!/usr/bin/env python3

import sys

with open(sys.argv[1], "r") as f:
    content = f.read().strip()
if content.count('\n') > 3:
    sys.stderr.write(f"File too long\n")
    exit(0)
for kw in [":", ";", "eval"]:
    if kw in content:
        sys.stderr.write(f"'{kw}' used\n")
        exit(0)
