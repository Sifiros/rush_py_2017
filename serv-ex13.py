#!/usr/bin/python3

import json
import hashlib
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        key = self.path.strip("/").split("/")[0]
        if not key:
            self.send_error(404)
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        h = hashlib.md5(key.encode()).hexdigest()
        now = datetime.today()
        past = (now - timedelta(days=int(h[:3], 16))).strftime("%A %d. %B %Y")
        future = (now + timedelta(days=int(h[-3:], 16))).strftime("%A %d. %B %Y")
        self.wfile.write(bytes(json.dumps({ "past": past, "future": future }), "utf8"))
        return

def run():
    print('starting server...')
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()
run()
