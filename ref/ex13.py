#!/usr/bin/env python3

import sys
import json
from datetime import datetime
import http.client

try:
    conn = http.client.HTTPConnection("127.0.0.1", 8081)
    conn.connect()
    conn.request("GET", "/" + sys.argv[1])
    response = conn.getresponse()
    data = json.loads(response.read())
    conn.close()
    future = datetime.strptime(data["future"], "%A %d. %B %Y")
    past = datetime.strptime(data["past"], "%A %d. %B %Y")
    print((future - past).days)
except:
    pass
