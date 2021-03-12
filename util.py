import logging
import smtplib
from email.message import EmailMessage

class EmailClient:
    def __init__(self, sender=None, password=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sender = sender
        self.password = password
        self.isTest = False
        if sender is None or password is None:
            self.isTest = True

    def send(self, recipient, subject, content):
        self.logger.info('sending email to {}'.format(recipient))
        self.logger.info('subject: {}'.format(subject))
        self.logger.info('content: {}'.format(content))

        if self.isTest:
            self.logger.info('email sent (test!)')
            return
        msg = EmailMessage()
        msg.set_content(content)

        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = recipient

        s = smtplib.SMTP(host='smtp.mail.yahoo.com', port=587)
        s.starttls()
        s.login(self.sender, self.password)
        s.send_message(msg)
        s.quit()

        self.logger.info('email sent')
