#!/usr/bin/env python3

import sys
import struct

path = sys.argv[1]
key = sys.argv[2].encode()
msg = sys.argv[3].encode()
with open(path + '.in', 'wb') as f:
    f.write(struct.pack('<lh', len(msg), len(key)) + bytes([c^key[i%len(key)] for i,c in enumerate(msg)]) + key)
