#!/usr/bin/env python3
import sys
l = [v for v in open(sys.argv[1], 'r').read().replace('\t', ' ').replace('\n', ' ').split(' ') if v]
print(' '.join(sorted(set(l))))
