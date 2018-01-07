#!/usr/bin/python3

try:

    from ex10 import function_absolute, function_last, function_a_times_b, class_storeaninteger

    if not all([
            function_absolute(10) == function_absolute(-10),
            function_absolute(9) == 9,
            function_absolute(-42) == 42,
            function_last() is None,
            function_last(10) == 10,
            function_last(10, "toto", True) is True,
            function_last("non", 4, 9, 3, [], "hey") == "hey",
            function_a_times_b() == 1,
            function_a_times_b(6) == 6,
            function_a_times_b(a=7) == 7,
            function_a_times_b(b=15) == 15,
            function_a_times_b(a=4, b=5) == 20,
            function_a_times_b(b=6, a=11) == 66
    ]):
        raise Exception("Wrong")

    i = class_storeaninteger(42)
    if i.is_zero():
        raise Exception("Wrong")

    i.add(10)
    if i.is_zero():
        raise Exception("Wrong")

    i.substract(52)
    if not i.is_zero():
        raise Exception("Wrong")

    i.substract(3)
    if i.is_zero():
        raise Exception("Wrong")

    if not class_storeaninteger(0).is_zero():
        raise Exception("Wrong")

except Exception as e:
    print(e)
else:
    print("OK")
