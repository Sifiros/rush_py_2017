#!/usr/bin/env python3

from modules import Verbose

import os
import json
import smtplib
from email import encoders
from email.utils import COMMASPACE, formatdate
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# @Verbose.FakeClass
@Verbose.Verbosable
class MailServer:
    def __init__(self, login, password, server="smtp.gmail.com", port=587, isTls=True):
        self.vprint(f"Creation of a mailserver for {login}")
        self.mail = login
        self.smtp = smtplib.SMTP(server, port)
        if isTls:
            self.smtp.starttls()
        self.smtp.login(login, password)
    def close(self):
        self.smtp.quit()
        self.vprint(f"Mailserver {self.mail}: Closed")
    @staticmethod
    def format_mail(mail):
        return mail + "@epitech.eu" * (not "@" in mail)
    def send(self, recipients, subject, text, files=[], sender=None):
        if type(recipients) is list:
            recipients = [ self.format_mail(recipient) for recipient in recipients ]
        else:
            recipients = self.format_mail(recipients)
        self.vprint(f'Mailserver {self.mail}: Sending "{subject}" to {recipients}')
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

def load(path, **kw):
    with open(path, "r") as f:
        return MailServer(**json.load(f), **kw)
