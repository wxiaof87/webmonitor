import logging
import smtplib
import json
import os
from email.message import EmailMessage


class EmailClient:
    def __init__(self, sender=None, password=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sender = sender
        self.password = password
        self.isTest = False
        if sender is None or password is None:
            cfg = self.loadConfig()
            if "sender" in cfg and "password" in cfg:
                self.sender, self.password = cfg["sender"], cfg["password"]
            else:
                self.isTest = True

    def loadConfig(self):
        cfg = {}
        configFileName = 'config.json'
        if not os.path.exists(configFileName):
            self.logger.warning("config file not found {} ".format(configFileName))
            return cfg

        with open(configFileName, 'r') as f:
            cfg = json.load(f)
            self.logger.info("loaded config: {}".format(cfg))
        return cfg

    def send(self, recipient, subject, content):
        self.logger.info('sending email to {}'.format(recipient))
        self.logger.info('subject: {}'.format(subject))
        self.logger.debug('content: {}'.format(content))

        if self.isTest:
            self.logger.info('email sent (test!)')
            return
        msg = EmailMessage()
        msg.set_content(content)

        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = recipient

        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls()
        s.login(self.sender, self.password)
        s.send_message(msg)
        s.quit()

        self.logger.info('email sent')
