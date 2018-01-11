#!/usr/bin/env python3

import csv
import yaml
import json

path = 'data-ex07'
with open(path + '.csv', 'r') as f:
     lines = list(csv.reader(f))
dico = { name : [line[i] for line in lines[1:]] for i, name in enumerate(lines[0]) }
for module, ext in [(yaml, 'yml'), (json, 'json')]:
     with open(path + '.' + ext, 'w') as f:
          module.dump(dico, f)
