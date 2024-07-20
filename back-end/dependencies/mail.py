from . import database as db, helpers as h, contracts as c
import configparser
import sys
import os
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException


def send_verification_email(account_id):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    try:
        cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
        cfile.read(os.path.join(sys.path[0], "config.ini"))

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = cfile["SMTP"]["MAIL_USER"]
        smtp_password = cfile["SMTP"]["MAIL_PASS"]

    except Exception as err:
        print(err)
        return ;

    # Create the email message
    stmt = "SELECT account_id, first_name, last_name, email, user_role FROM accounts WHERE account_id = %s"
    db.cursor.execute(stmt, (account_id,))
    res = db.cursor.fetchone()
    account_data = {
        "account_id": res[0],
        "first_name": res[1],
        "last_name": res[2],
        "email": res[3],
        "user_role": res[4]
    }

    token = h.create_jwt_token(account_data.get("account_id"), account_data.get("user_role"), 1800)

    html = f"""
    <html>
      <body>
        <p>Hi, {account_data.get("first_name")} {account_data.get("last_name")} (Account ID: {account_data.get("account_id")}),<br>
          This email is from Alex Bank regarding verification of your email. Please note that this token is valid only 30 mins. <br>
          If you made this request, please click on the link below: </p>
        <p><a href="https://alex-bank.com/verify.html?token={token}">Verify Your Alex Bank Account</a></p>
        <p> If you did not make such request, please ignore this email. </p>
        <br>
        <p>Sincerely, </p>
        <p>Alex Bank </p>
      </body>
    </html>
    """
    body = f"""Hi, {account_data.get("first_name")} {account_data.get("last_name")} (Account ID: {account_data.get("account_id")}), \n"
    This email is from Alex Bank regarding verification of your email. Please note that this token is valid only 30 mins. If you made this request, please click on the link below: \n
    https://alex-bank.com/verify.html?token={token} \n
    If you did not make such request, please ignore this email. \n\nSincerely, \nAlex Bank
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = account_data.get("email")
    msg["Subject"] = f"{account_data.get('first_name')} - Verify Your Email"

    part1 = MIMEText(body, "plain")
    part2 = MIMEText(html, "html")
    msg.attach(part1)
    msg.attach(part2)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_password_reset_email(account_id):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    try:
        cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
        cfile.read(os.path.join(sys.path[0], "config.ini"))

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = cfile["SMTP"]["MAIL_USER"]
        smtp_password = cfile["SMTP"]["MAIL_PASS"]

    except Exception as err:
        print(err)
        return ;

    db.cursor.execute("SELECT account_id, user_role, first_name, last_name, email FROM accounts WHERE account_id = %s",
                      (account_id,))
    if db.cursor.rowcount != 1:
        raise HTTPException(404, f"User {account_id} not found!")
    row = db.cursor.fetchone()

    if row[4] is None:
        raise HTTPException(404, f"No email address found for Account {row[0]}.")

    token = h.create_jwt_token(row[0], row[1], 1800)

    html = f"""
        <html>
          <body>
            <p>Hi, {row[2]} {row[3]} (Account ID: {row[0]}),<br>
              Your password has been reset. From the provided link below, you can change your password. Note that it is valid only for 30 mins. <br>
            <p><a href="https://alex-bank.com/reset-password.html?token={token}">Reset Your Alex Bank Password</a></p>
            <p> If you did not make such request, please ignore this email. </p>
            <br>
            <p>Sincerely, </p>
            <p>Alex Bank </p>
          </body>
        </html>
        """
    body = f"""Hi, {row[2]} {row[3]} (Account ID: {row[0]}), \n"
        Your password has been reset. From the provided link below, you can change your password. Note that it is valid only for 30 mins. \n
        https://alex-bank.com/reset-password.html?token={token} \n
        If you did not make such request, please ignore this email. \n\nSincerely, \nAlex Bank
        """

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = row[4]
    msg["Subject"] = f"{row[2]} - Reset Your Password"

    part1 = MIMEText(body, "plain")
    part2 = MIMEText(html, "html")
    msg.attach(part1)
    msg.attach(part2)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_contract_email(product_uid: int, email: str = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    if email is None:
        stmt = """SELECT 
                    ac.email, ac.first_name, ac.last_name, pi.contract_id, pr.name
                FROM product_instances pi
                JOIN accounts ac 
                  ON ac.account_id = pi.account_id
                JOIN applications appl
                  ON appl.application_id = pi.application_id
                JOIN products pr
                  ON pr.product_id = appl.product_id
                WHERE pi.product_uid = %s
        """
        db.cursor.execute(stmt, (product_uid,))
        result = db.cursor.fetchone()
        if result is None:
            print(f"No data found for product_uid: {product_uid}")
            return  # or handle this case as required
        email, first_name, last_name, contract_id, product_name = result

    try:
        cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
        cfile.read(os.path.join(sys.path[0], "config.ini"))

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = cfile["SMTP"]["MAIL_USER"]
        smtp_password = cfile["SMTP"]["MAIL_PASS"]

    except Exception as err:
        print(err)
        return

    pdf_file = c.contract_buffer(contract_id)  # Updated to use contract_id
    if pdf_file is None:
        print(f"Failed to generate contract for contract_id: {contract_id}")
        return

    # Email content
    from_email = "smpt.alex.bank.com@gmail.com"
    to_email = email
    subject = f"Contract for {product_name} {product_uid}"
    body = f"Dear {first_name} {last_name}, \n\n" \
           f"Please find attached, your contract (Contract ID: {contract_id}) with Alex Bank for Product UID: " \
           f"{product_uid}.\n\n" \
           f"Sincerely,\n" \
           f"Alex Bank"

    # Create the email message
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Create PDF and attach it to the email
    pdf_buffer = pdf_file
    pdf_name = f"contract_{contract_id}.pdf"
    msg.add_attachment(pdf_buffer.read(), maintype="application", subtype="pdf", filename=pdf_name)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_product_status_update_email(product_uid: int, new_status: str):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    try:
        cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
        cfile.read(os.path.join(sys.path[0], "config.ini"))

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = cfile["SMTP"]["MAIL_USER"]
        smtp_password = cfile["SMTP"]["MAIL_PASS"]

    except Exception as err:
        print(err)
        return


    stmt = """
    SELECT pi.product_uid, ac.email, ac.first_name, ac.last_name, p.name, ps.status_name
    FROM product_instances pi 
    JOIN accounts ac ON pi.account_id = ac.account_id
    JOIN applications appl ON appl.application_id = pi.application_id
    JOIN products p ON p.product_id = appl.product_id
    JOIN product_statuses ps ON ps.code = pi.status_code
    WHERE pi.product_uid = %s"""

    db.cursor.execute(stmt, (product_uid,))
    if db.cursor.rowcount != 1:
        return
    row = db.cursor.fetchone()

    data = {
        "product_uid": row[0],
        "email": row[1],
        "first_name": row[2],
        "last_name": row[3],
        "product_name": row[4],
        "status_name": row[5]
    }
    styling = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Application Confirmation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: var(--color-bg-light, rgb(254, 254, 254));
                color: #222222;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .header {
                text-align: center;
                color: #000;
                border-radius: 5px;
                padding: 10px 0;
            }
            .content {
                margin: 20px 0;
            }
            .footer {
                text-align: center;
                font-size: 12px;
                color: var(--color-grey-dark, #979797);
                margin-top: 20px;
            }
            .status {
                color: rgb(131, 152, 162);
                font-weight: bold;
            }
            .button {
                background-color: rgb(131, 152, 162);
                color: rgb(254, 254, 254);
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
            }
        </style>
    </head>
    """

    if new_status == "APL":
        content = f"""
        <body>
            <div class="container">
                <div class="header">
                    <h1>Application Received</h1>
                </div>
                <div class="content">
                    <p>Dear {data.get("first_name")} {data.get("last_name")},</p>
                    <p>Thank you for applying for the {data.get("product_name")}. We have successfully received your application and it is currently under review. Your Product UID is {data.get("product_uid")}.</p>
                    <p>We appreciate your interest and will get back to you shortly with the next steps. You can always follow the status of your product and make changes to it at <a href="https://alex-bank.com/myaccount/product.html?product_uid={data.get("product_uid")}">Alex Bank (Product UID: {data.get("product_uid")})</a></p>
                    <p>In the meantime, if you have any questions or need further assistance, please do not hesitate to contact us.</p>
                    <p>Best regards,</p>
                    <p>Alex Bank</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Alex Bank. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        body = f"Dear {data.get('first_name')} {data.get('last_name')},\n\n"
        "Thank you for applying for the {data.get('product_name')}. We have successfully received your application and it is currently under review. Your Product UID is {data.get('product_uid')}.\n\n"
        "We appreciate your interest and will get back to you shortly with the next steps. You can always follow the status of your product and make changes to it at Alex Bank (Product UID: {data.get('product_uid')}): https://alex-bank.com/myaccount/product.html?product_uid={data.get('product_uid')}\n\n"
        "In the meantime, if you have any questions or need further assistance, please do not hesitate to contact us.\n\n"
        "Best regards,\n"
        "Alex Bank"
    else:
        content = f"""
        <body>
            <div class="container">
                <div class="header">
                    <h1>Product Status Update</h1>
                </div>
                <div class="content">
                    <p>Dear {data.get("first_name")} {data.get("last_name")},</p>
                    <p>We are pleased to inform you that the status of your product has been updated. Please find the details below:</p>
                    <p>Product UID: <strong>{data.get("product_uid")}</strong> ({data.get("product_name")})</p>
                    <p>Updated Status: <span class="status">{data.get("status_name")}</span></p>
                    <a href="https://alex-bank.com/myaccount/product.html?product_uid={data.get("product_uid")}" class="button" style="color: rgb(254, 254, 254);">View Product</a>
                    <br> <br>
                    <p>Best,</p>
                    <p>Alex Bank</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Alex Bank. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        body = f"Dear {data.get('first_name')} {data.get('last_name')},\n\nWe are pleased to inform you that the status of your product has been updated. Please find the details below:\n\nProduct UID: {data.get('product_uid')} ({data.get('product_name')})\n\nUpdated Status: {data.get('status_name')}\n\nView Product: https://alex-bank.com/myaccount/product.html?product_uid={data.get('product_uid')}\n\nBest,\n\nAlex Bank"

    html = styling + content

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = data.get("email")
    msg["Subject"] = f"{data.get('product_uid')} - Status Update: {data.get('status_name')}"

    part1 = MIMEText(body, "plain")
    part2 = MIMEText(html, "html")
    msg.attach(part1)
    msg.attach(part2)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

    ...

