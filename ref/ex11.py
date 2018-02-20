#!/usr/bin/env python3

import sys
import hashlib

print(hashlib.md5(str(sum(int(arg) for arg in sys.argv[1:])).encode()).hexdigest())

