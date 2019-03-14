from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# to use a virtual server instead: python -m smtpd -n -c DebuggingServer localhost:8025
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    # mail.send(msg)
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
