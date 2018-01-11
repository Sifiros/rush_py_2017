#!/usr/bin/env python3

import os
import json
import time
import signal
import docker
import shutil
import struct
import smtplib
import subprocess
from email import encoders
from datetime import datetime
from email.utils import COMMASPACE, formatdate
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict
from contextlib import closing

class Json(object):
    class Internal:
        def __init__(self, d):
            self._keys = sorted(list(d.keys()))
            self.__dict__.update({ k: Json(v) for k, v in d.items()})
        def __str__(self):
            return str(self.__dict__)
        def __repr__(self):
            return repr(self.__dict__)
        def __contains__(self, key):
            return key in self._keys
        def get(self, value, default=None):
            return self.__dict__[value] if value in self else default
        def iteritems(self):
            for key in self._keys:
                yield key, self.__dict__[key]
    def __new__(cls, o):
        if type(o) is list:
            return [Json(e) for e in o]
        if type(o) is dict:
            return Json.Internal(o)
        return o
    @staticmethod
    def load(path):
        with open(path, "r") as f:
            return Json(json.load(f))

class Git:
    @staticmethod
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

def VerboseFakeClass(cls):
    def p(name):
        return lambda *args, **kw: print(f"{cls.__name__}.{name} {args[1:]} {kw}")
    for name, attr in cls.__dict__.items():
        if callable(attr):
            setattr(cls, name, p(name))
    return cls

# @VerboseFakeClass
class MailServer:
    def __init__(self, login, password, server="smtp.gmail.com", port=587, isTls=True):
        self.mail = login
        self.smtp = smtplib.SMTP(server, port)
        if isTls:
            self.smtp.starttls()
        self.smtp.login(login, password)
    def close(self):
        self.smtp.quit()
    def send(self, recipients, subject, text, files=[], sender=None):
        sender = self.mail if sender is None else sender
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = COMMASPACE.join(recipients) if type(recipients) is list else recipients
        msg['Date'] = formatdate(localtime = True)
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        for path in files:
            if type(path) is tuple:
                name, content = path
            else:
                with open(path, 'rb') as file:
                    content = file.read()
                name = os.path.basename(path)
            part = MIMEBase('application', "octet-stream")
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{name}"')
            msg.attach(part)
        self.smtp.sendmail(sender, recipients, msg.as_string())
    @staticmethod
    def load(path):
        with open(path, "r") as f:
            return MailServer(**json.load(f))

class TriggerableContext:
    def __init__(self):
        self.triggered = False
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return
    def trigger(self, triggered=True):
        self.triggered = triggered

class Timeout(TriggerableContext):
    class TimeoutException(Exception):
        pass
    _used = False
    @staticmethod
    def _handler(signum, frame):
      raise Timeout.TimeoutException()
    def __init__(self, seconds=0):
        super().__init__()
        self.seconds = seconds
    def __enter__(self):
        if Timeout._used:
            raise RuntimeError("Timeout contexts can't be nested")
        Timeout._used = True
        signal.signal(signal.SIGALRM, self._handler)
        signal.alarm(self.seconds)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
        Timeout._used = False
        self.trigger(exc_type is Timeout.TimeoutException)
        return exc_type is None or self.triggered

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
    def restart(self):
        self.docker.restart(timeout=0)
    def close(self):
        self.docker.remove(force=True)
    def run(self, cmd, stdout="/dev/null", stdin="/dev/null", detach=False):
        output = Container.Output(self.docker.exec_run([
            "bash", "-c", " ".join(f'"{arg}"' for arg in cmd) + f" < {stdin} > {stdout}"
        ], socket=True))
        return output if detach else output.get()

class Mouli():
    def __init__(self, config_path, mailserver_path):
        self.config = Json.load(config_path)
        self.mailserver = MailServer.load(mailserver_path)
    def close(self):
        self.mailserver.close()
    def clone(self, mail):
        return Git.clone(mail, self.config.repository.name, self.config.repository.path)
    def iterclone(self, mails):
        return ((mail, self.clone(mail)) for mail in mails)
    def send_mail(self, mail, message, filecontent):
        now = datetime.today().strftime('%Y/%m/%d %H:%M')
        self.mailserver.send(mail, f"[Mouli] {self.config.name} {now}", message,
                             files=[("trace.txt", filecontent)])
    def get_closing_container(self):
        mps = self.config.mountpoints
        return closing(Container(volumes=[(mps.local, mps.remote)], working_dir=mps.remote))
    def copyfile(self, mail, oldpath, new):
        repo = self.config.repository
        repopath = os.path.join(repo.path, repo.name, mail)
        newpath = self.config.mountpoints.local
        if new is not None:
            newpath = os.path.join(newpath, new)
        if oldpath.startswith("$"):
            oldpath = os.path.join(repopath, oldpath[1:])
        shutil.copy2(oldpath, newpath)
    def copyfiles(self, mail, files):
        for old, new in files if type(files) is list else files.iteritems():
            self.copyfile(mail, old, new)
    def docker_exec(self, container, binary, config, **kwargs):
        kw = { key: config.get(key) for key in ["stdin", "stdout"] if key in config }
        kw.update(kwargs)
        return container.run([binary] + config.get("args", []), **kw)
    def docker_reset(self, container):
        container.restart()
        return container.run(["rm", "-rf", os.path.join(self.config.mountpoints.remote, "*")])
    def run_test(self, mail, container, test, binarylocal, binaryremote, diff_services,
                 timeout=TriggerableContext()):
        self.copyfile(mail, binarylocal, binaryremote)
        with timeout:
            error = self.docker_exec(container, binaryremote, test)
            for diff_service in diff_services:
                diff_service.get()
        if timeout.triggered:
            return f"Timeout after {timeout.seconds}s.", {}
        if error is not None:
            return error, {}
        result = {}
        for filepath in test.cmpfiles:
            try:
                with open(os.path.join(self.config.mountpoints.local, filepath), "r") as f:
                    content = f.read().strip()
            except Exception as e:
                return str(e), {}
            result[filepath] = content
        return None, result
    def _run_setup(self):
        mps = self.config.mountpoints
        if os.path.exists(mps.local):
            shutil.rmtree(mps.local)
            os.mkdir(mps.local)
    def _run_testgroup_setup(self, container, testgroup):
        self.docker_reset(container)
        self.copyfiles(mail, testgroup.copy)
        for service in testgroup.services:
            self.docker_exec(container, service.binary, service, detach=True)
            time.sleep(service.wait)
    def _parse_run_result(self, results):
        short = ""
        detail = ""
        tests = 0
        working = 0
        for testgroup_name, testgroup in self.config.testgroups.iteritems():
            short += f"{testgroup_name}\n"
            detail += f"{'-'*10}{testgroup_name}{'-'*10}\n\n"
            for test_name, test in testgroup.tests.iteritems():
                tests += 1
                result = results[testgroup_name][test_name]
                detail += f"\t{test_name}: "
                test_code = "KO"
                if result.error[0]:
                    detail += f"Error\n\n{result.error[0]}"
                elif result.output[0] != result.output[1]:
                    detail += "Output differs"
                    for cmpfile in test.cmpfiles:
                        cmp0 = result.output[0][cmpfile]
                        cmp1 = result.output[1][cmpfile]
                        if cmp0 != cmp1:
                            detail += f"\n\nGot:\n{'>'*5}\n{cmp0}\n{'<'*5}"
                            detail += f"\n\nExpected:\n{'>'*5}\n{cmp1}\n{'<'*5}"
                else:
                    working += 1
                    test_code = "OK"
                    detail += "Test Passed"
                short += f"\t{test_name}: {test_code}\n"
                detail += "\n\n"
        return working / tests, short, detail
    def run_tests(self, mail):
        self._run_setup()
        with self.get_closing_container() as container:
            results = defaultdict(lambda: defaultdict(lambda: Json({
                "error": [None, None],
                "output": defaultdict(lambda: ["", ""])
            })))
            for testgroup_name, testgroup in self.config.testgroups.iteritems():
                for ref, (binary, timeout) in enumerate([(testgroup.totest, Timeout(testgroup.timeout)),
                                                         (testgroup.reference, TriggerableContext())]):
                    self._run_testgroup_setup(container, testgroup)
                    for test_name, test in testgroup.tests.iteritems():
                        diff_services = [
                            self.docker_exec(container, service.binary, service, detach=True)
                            for service in testgroup.diff_services
                        ]
                        error, output = self.run_test(
                            mail, container, test, binary, testgroup.binary,
                            diff_services, timeout
                        )
                        results[testgroup_name][test_name].error[ref] = error
                        results[testgroup_name][test_name].output[ref] = output
        return self._parse_run_result(results)

# students = ["chicha_j"]
# students = ["julien.chicha@epitech.eu"]

# with closing(Mouli("conf/mouli.json", "conf/mailserver.json")) as mouli:
#     for mail, error in mouli.iterclone(students):
#         if error is not None:
#             mouli.send_mail(mail, "Unable to clone", error)
#             print(None)
#         else:
#             score, short, detail = mouli.run_tests(mail)
#             mouli.send_mail(mail, short, detail)
#             print(score)
