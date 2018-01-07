#!/usr/bin/python3

try:
    dico = {}
    while True:
        name, word = tuple(input("dico> ").split(":"))
        if name in dico:
            dico[name] += word
        else:
            dico[name] = word
        print(name + ":" + dico[name])
except:
    pass
