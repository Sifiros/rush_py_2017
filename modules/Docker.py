#!/usr/bin/env python3

from modules import Verbose

import os
import docker

@Verbose.Verbosable
class Container:
    class Output:
        def __init__(self, sock):
            self.sock = sock
        def get(self):
            try:
                return next(docker.utils.socket.frames_iter(self.sock)).decode().strip()
            except StopIteration:
                return None
    client = docker.from_env()
    def __init__(self, image='python:3', *args, **kwargs):
        self.vprint(f'Creation of a "{image}" container')
        kw = {
            "auto_remove": True,
            "privileged": True,
            "user": os.getuid(),
            "detach": True,
            "tty": True
        }
        kw.update(kwargs)
        self.volumes = []
        d = {}
        for local, remote in kw.get("volumes", []):
            d[local] = { "bind": remote, "mode": "rw" }
            if not os.path.isdir(local):
                os.mkdir(local)
            self.volumes.append(local)
        kw["volumes"] = d
        self.docker = Container.client.containers.run(image, *args, **kw)
        self.vprint(f"Container {self.docker.short_id}: Created")
    def restart(self):
        self.vprint(f"Container {self.docker.short_id}: Restarting")
        self.docker.restart(timeout=0)
    def close(self):
        self.docker.remove(force=True)
        self.vprint(f"Container {self.docker.short_id}: Removed")
    def run(self, cmd, stdout="/dev/null", stdin="/dev/null", detach=False):
        self.vprint(
            f'Container {self.docker.short_id}: Running a{" detached" if detach else ""} command'
        )
        output = Container.Output(self.docker.exec_run([
            "bash", "-c", " ".join(f'"{arg}"' for arg in cmd) + f" < {stdin} > {stdout}"
        ], socket=True))
        return output if detach else output.get()
