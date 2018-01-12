#!/usr/bin/env python3

import os
import shutil
import subprocess

def clone(login, repo, path="."):
    if not os.path.isdir(path):
        os.makedirs(path)
    path = os.path.join(path, repo, login)
    if os.path.exists(path):
        shutil.rmtree(path)
    p = subprocess.Popen(
        [ "git", "clone", f"git@git.epitech.eu:/{login}/{repo}", path ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    if p.returncode:
        return err.decode()
