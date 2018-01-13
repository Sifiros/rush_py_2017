#!/usr/bin/env python3

import os

def makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

makedirs("resources/ex08/directory_empty/")
makedirs("resources/ex08/directory_content/content01/")
makedirs("resources/ex08/directory_content/content02/")
makedirs("resources/ex08/directory_content/content03/")
