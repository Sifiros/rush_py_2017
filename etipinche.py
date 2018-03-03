#!/usr/bin/env python3

import json
from modules import Mouli

def get_students(path, group_count, group_idx):
    with open(path, 'r') as f:
        student_logins = [line.split(';')[0] for line in f.read().strip().split('\n')]
    group_size = int(len(student_logins) / group_count)
    begin = group_idx * group_size
    end = None if group_idx >= group_count - 1 else begin + group_size
    return student_logins[slice(begin, end)]

student_logins = get_students('students.csv', 2, 0)
#student_logins = ["vigand_q"]

with Mouli.load_closing_context("conf/mouli.json", "conf/mailserver.json", verbose=True) as mouli:
    results = mouli.clone_and_test(student_logins, send=True)

with open('/tmp/mouli.out', 'w') as f:
    json.dump(results, f, indent=4)
