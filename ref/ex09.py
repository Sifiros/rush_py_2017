#!/usr/bin/env python3

import sys
import struct

try:
    path = sys.argv[1]
    with open(path + '.in', 'rb') as f:
        data = f.read()
    headsz = struct.calcsize('<lh')
    msgsz, keysz = struct.unpack('<lh', data[:headsz])
    msg = data[headsz:][:msgsz]
    key = data[headsz+msgsz:]
    with open(path + '.out', 'wb') as f:
        f.write(bytes([c^key[i%len(key)] for i,c in enumerate(msg)]))
except:
    pass
