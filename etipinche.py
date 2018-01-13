#!/usr/bin/env python3

from modules import Mouli

student_logins = ["chicha_j"]

with Mouli.load_closing_context("conf/mouli.json", "conf/mailserver.json", verbose=True) as mouli:
    results = mouli.clone_and_test(student_logins, send=True)
print(results)
