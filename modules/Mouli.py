#!/usr/bin/env python3

from modules import Git
from modules import Verbose
from modules import JsonObject
from modules import MailServer
from modules.Trigger import TriggerableContext, Timeout
from modules.Docker import Container

import os
import time
import shutil
import subprocess
from datetime import datetime
from collections import defaultdict
from contextlib import closing

class MsgError(BaseException):
    pass

@Verbose.Verbosable
class Mouli():
    def __init__(self, config_path, mailserver_path):
        self.config = JsonObject.load(config_path)
        self.vprint(f'Creation of a "{self.config.name}" mouli')
        self.mailserver = MailServer.load(mailserver_path, verbose=self.verbose)
    def close(self):
        self.mailserver.close()
        self.vprint(f'Mouli "{self.config.name}": Closed')
    def clone(self, mail):
        self.vprint(f'Mouli "{self.config.name}": Cloning {mail} repository')
        return Git.clone(mail, self.config.repository.name, self.config.repository.path)
    def iterclone(self, mails):
        return ((mail, self.clone(mail)) for mail in mails)
    def send_mail(self, mail, message, filecontent):
        now = datetime.today().strftime('%Y/%m/%d %H:%M')
        self.mailserver.send(mail, f"[Mouli] {self.config.name} {now}", message,
                             files=[("trace.txt", filecontent)])
    def get_closing_container(self):
        mps = self.config.mountpoints
        return closing(Container(
            "chichaj/mouli",
            volumes=[(mps.local, mps.remote)],
            working_dir=mps.remote,
            verbose=self.verbose
        ))
    def get_real_path(self, mail, path):
        repo = self.config.repository
        repopath = os.path.join(repo.path, repo.name, mail)
        if path.startswith("$"):
            return os.path.join(repopath, path[1:])
        return path
    def copyfile(self, mail, oldpath, new):
        self.vprint(f'Mouli "{self.config.name}": Copying {oldpath}')
        newpath = self.config.mountpoints.local
        if new is not None:
            newpath = os.path.join(newpath, new)
        oldpath = self.get_real_path(mail, oldpath)
        cp = shutil.copy2
        if os.path.isdir(oldpath):
            cp = shutil.copytree
        cp(oldpath, newpath)
    def copyfiles(self, mail, files):
        for old, new in files if type(files) is list else files.iteritems():
            self.copyfile(mail, old, new)
    def docker_exec(self, container, binary, config, **kwargs):
        self.vprint(f'Mouli "{self.config.name}": Executing {binary}')
        kw = { key: config.get(key) for key in ["stdin", "stdout"] if key in config }
        kw.update(kwargs)
        return container.run([binary] + config.get("args", []), **kw)
    def docker_reset(self, container):
        container.run(["rm", "-rf"] + [
            os.path.join(self.config.mountpoints.remote, path)
            for path in os.listdir(self.config.mountpoints.local)
        ])
        container.restart()
    def run_test(self, mail, container, test, binarylocal, binaryremote, diff_services,
                 timeout=TriggerableContext()):
        self.copyfile(mail, binarylocal, binaryremote)
        with timeout:
            error = self.docker_exec(container, binaryremote, test)
            self.vprint(f'Mouli "{self.config.name}": Joining "Diff services"')
            for diff_service in diff_services:
                diff_service.get()
        if timeout.triggered:
            self.vprint(f'Mouli "{self.config.name}": Test Timeout')
            return f"Timeout after {timeout.seconds}s.", {}
        if error is not None:
            self.vprint(f'Mouli "{self.config.name}": Test Error')
            return error, {}
        result = {}
        for filepath in test.get("cmpfiles", []):
            try:
                with open(os.path.join(self.config.mountpoints.local, filepath), 'rb') as f:
                    content = f.read().strip()
            except Exception as e:
                return str(e), {}
            result[filepath] = content
        return None, result
    def _run_setup(self):
        self.vprint(f'Mouli "{self.config.name}": Setup')
        mps = self.config.mountpoints
        if os.path.exists(mps.local):
            shutil.rmtree(mps.local)
            os.mkdir(mps.local)
    def _run_testgroup_setup(self, mail, container, testgroup):
        self.docker_reset(container)
        if testgroup.get("copy"):
            self.copyfiles(mail, testgroup.copy)
        for service in testgroup.get("services", []):
            self.docker_exec(container, service.binary, service, detach=True)
            time.sleep(service.wait)
    def _parse_run_result(self, results):
        self.vprint(f'Mouli "{self.config.name}": Generating formatted result')
        short = ""
        detailed = ""
        tests = 0
        working = 0
        for testgroup_name, testgroup in self.config.testgroups.iteritems():
            short += f"{testgroup_name}\n"
            detailed += f"{'-'*10}{testgroup_name}{'-'*10}\n\n"
            for test_name, test in testgroup.tests.iteritems():
                tests += 1
                result = results[testgroup_name][test_name]
                detailed += f"\t{test_name}: "
                test_code = "KO"
                if result.error[0]:
                    detailed += f"Error\n\n{result.error[0]}"
                elif result.error[1]:
                    detailed += f"Internal Error\n\n{result.error[1]}"
                elif result.output[0] != result.output[1]:
                    detailed += "Output differs"
                    for cmpfile in test.cmpfiles:
                        cmp0 = result.output[0][cmpfile]
                        cmp1 = result.output[1][cmpfile]
                        if cmp0 != cmp1:
                            try:
                                if len(cmp0) > 10000 or len(cmp1) > 10000:
                                    raise MsgError()
                                cmp0 = cmp0.decode()
                                cmp1 = cmp1.decode()
                            except (UnicodeError, MsgError) as e:
                                detailed += f"\n\n'{cmpfile}' differ but is unprintable"
                            else:
                                detailed += f"\n\nGot:\n{'>'*5}\n{cmp0}\n{'<'*5}"
                                detailed += f"\n\nExpected:\n{'>'*5}\n{cmp1}\n{'<'*5}"
                else:
                    working += 1
                    test_code = "OK"
                    detailed += "Test Passed"
                short += f"\t{test_name}: {test_code}\n"
                detailed += "\n\n"
        return working / tests if tests else None, short, detailed
    def _pretests(self, tests, binary, *args):
        if tests:
            self.vprint(f'Mouli "{self.config.name}": Running pretests for {binary}')
        for test in tests:
            out, err = subprocess.Popen([test, binary], stderr=subprocess.PIPE).communicate()
            if err:
                return err.decode()
    def _run_tests_unsecure(self, mail, container, results, validated):
        for testgroup_name, testgroup in self.config.testgroups.iteritems():
            if testgroup_name in validated:
                continue
            self.vprint(
                f'Mouli "{self.config.name}": Running "{testgroup_name}" grouptest for {mail}'
            )
            for ref, (binary, timeout) in enumerate(
                    [(testgroup.totest, Timeout(testgroup.get("timeout", 2))),
                     (testgroup.reference, TriggerableContext())]
            ):
                self.vprint(f'Mouli "{self.config.name}": {"Reference" if ref else "Test"} mode')
                try:
                    error = self._pretests(testgroup.get("pretests", []),
                                           self.get_real_path(mail, binary))
                    if error:
                        raise AssertionError(error)
                    self._run_testgroup_setup(mail, container, testgroup)
                    for test_name, test in testgroup.tests.iteritems():
                        self.vprint(
                            f'Mouli "{self.config.name}": Running "{test_name}" test for {mail}'
                        )
                        diff_services = [
                            self.docker_exec(container, service.binary, service, detach=True)
                            for service in testgroup.get("diff_services", [])
                        ]
                        error, output = self.run_test(
                            mail, container, test, binary, testgroup.get("binary", "./binary"),
                            diff_services, timeout
                        )
                        results[testgroup_name][test_name].error[ref] = error
                        results[testgroup_name][test_name].output[ref] = output
                except (FileNotFoundError, AssertionError) as e:
                    self.vprint(
                        f'Mouli "{self.config.name}": Test failure'
                    )
                    for test_name, test in testgroup.tests.iteritems():
                        results[testgroup_name][test_name].error[ref] = e
                        results[testgroup_name][test_name].output[ref] = None
            validated.append(testgroup_name)
    def run_tests(self, mail):
        self.vprint(f'Mouli "{self.config.name}": Running tests for {mail}')
        self._run_setup()
        results = defaultdict(lambda: defaultdict(lambda: JsonObject.Json({
            "error": [None, None],
            "output": defaultdict(lambda: ["", ""])
        })))
        validated = []
        while True:
            try:
                with self.get_closing_container() as container:
                    self._run_tests_unsecure(mail, container, results, validated)
            except Exception as e:
                self.vprint(f'Mouli "{self.config.name}": Encountered an error "{e}"')
            else:
                break
        return self._parse_run_result(results)
    def clone_and_test(self, mails, send=False):
        self.vprint(f'Mouli "{self.config.name}": Starting phase of "clone and test"')
        results = {}
        for mail, error in self.iterclone(mails):
            if error is not None:
                score = None
                short = "Unable to clone"
                detailed = error
            else:
                score, short, detailed = self.run_tests(mail)
            results[mail] = { "score": score, "short": short, "detailed": detailed }
            if send:
                self.send_mail(mail, short, detailed)
        return results

def load_closing_context(*args, **kw):
    return closing(Mouli(*args, **kw))
