#!/usr/bin/python3

import sys

try:
    while True:
        print(eval(input("bistro> ")))
except SyntaxError as e:
    print("Bad Syntax")
except KeyboardInterrupt as e:
    print("Ctrl + C")
except Exception as e:
    print(e)
