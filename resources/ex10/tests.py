#!/usr/bin/env python3

def test(module):
    if not all([
            module.function_absolute(10) == module.function_absolute(-10),
            module.function_absolute(9) == 9,
            module.function_absolute(-42) == 42,
            module.function_last() is None,
            module.function_last(10) == 10,
            module.function_last(10, "toto", True) is True,
            module.function_last("non", 4, 9, 3, [], "hey") == "hey",
            module.function_a_times_b() == 1,
            module.function_a_times_b(6) == 6,
            module.function_a_times_b(a=7) == 7,
            module.function_a_times_b(b=15) == 15,
            module.function_a_times_b(a=4, b=5) == 20,
            module.function_a_times_b(b=6, a=11) == 66
    ]):
        raise Exception("Wrong")
    i = module.class_storeaninteger(42)
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
    
    if not module.class_storeaninteger(0).is_zero():
        raise Exception("Wrong")
