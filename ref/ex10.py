#!/usr/bin/python3

def function_absolute(i):
    return abs(i)

def function_last(*args):
    return args[-1] if args else None

def function_a_times_b(a=1, b=1):
    return a * b

class class_storeaninteger:

    def __init__(self, i):
        self.i = i

    def is_zero(self):
        return self.i == 0

    def add(self, i):
        self.i += i

    def substract(self, i):
        self.i -= i
