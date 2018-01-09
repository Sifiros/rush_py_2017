#!/usr/bin/python3

import os
import json
import shutil
import smtplib
import subprocess
from email import encoders
from datetime import datetime
from email.utils import COMMASPACE, formatdate
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from contextlib import closing

class Json(object):
    class Internal:
        def __init__(self, d):
            self.__dict__.update({ k: Json(v) for k, v in d.items()})
        def __str__(self):
            return str(self.__dict__)
        def __repr__(self):
            return repr(self.__dict__)
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
        self.mailserver.send(mail, f"[Mouli] {self.config.project} {now}", message,
                             files=[("trace.txt", filecontent)])

# students = ["chicha_j"]
# students = ["julien.chicha@epitech.eu"]

# with closing(Mouli("conf/mouli.json", "conf/mailserver.json")) as mouli:
#     for mail, error in mouli.iterclone(students):
#         if error is not None:
#             mouli.send_mail(mail, "Build Failed", error)
#         else:
#             print("OK")
