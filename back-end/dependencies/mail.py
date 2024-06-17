from . import database as db
import configparser
import sys
import os
import smtplib
from email.message import EmailMessage


def send_verification_email(account_id):
    try:
        cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
        cfile.read(os.path.join(sys.path[0], "config.ini"))

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_user = cfile["SMTP"]["MAIL_USER"]
        smtp_password = cfile["SMTP"]["MAIL_PASS"]

    except Exception as err:
        print(err)
        return;

    # Create the email message

    body = "Yo, hello!"

    msg = EmailMessage()
    msg['From'] = smtp_user
    msg['To'] = "alex05.yordanov@gmail.com"
    msg['Subject'] = "Test from the server"
    msg.set_content(body)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print('Email sent successfully.')
    except Exception as e:
        print(f'Failed to send email: {e}')


