import smtplib
from email.message import EmailMessage

def notify(subject, content):
    # TODO: add this as parameters or load from config file
    sender = 'sender@xxx.com'
    password = 'addpassword'
    recipient = 'recipient@yyy.com'


    msg = EmailMessage()
    msg.set_content(content)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP(host='smtp.mail.yahoo.com', port=587)
    s.starttls()
    s.login(sender, password)
    s.send_message(msg)
    s.quit()


if __name__ == '__main__':
    notify('test', 'it is a test')

