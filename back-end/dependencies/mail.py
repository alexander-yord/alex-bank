from . import database as db, helpers as h, contracts as c
import configparser
import sys
import os
import smtplib
import io
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch


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
    stmt = "SELECT account_id, first_name, last_name, email FROM accounts WHERE account_id = %s"
    db.cursor.execute(stmt, (account_id,))
    res = db.cursor.fetchone()
    account_data = {
        "account_id": res[0],
        "first_name": res[1],
        "last_name": res[2],
        "email": res[3]
    }

    token = h.generate_authorization()
    stmt = "INSERT into login_sessions (account_id, token) values (%s, %s)"
    account_token_tuple = (account_id, token)
    db.cursor.execute(stmt, account_token_tuple)
    db.cnx.commit()

    html = f"""
    <html>
      <body>
        <p>Hi, {account_data.get("first_name")} {account_data.get("last_name")} (Account ID: {account_data.get("account_id")}),<br>
          This email is from Alex Bank regarding verification of your email. <br>
          If you made this request, please click on the link below: </p>
        <p><a href="https://alex-bank.com/verify.html?token={token}">Verify Your Alex Bank Account</a></p>
        <p> If you did not make such request, please ignore this email. </p>
      </body>
    </html>
    """
    body = f"""Hi, {account_data.get("first_name")} {account_data.get("last_name")} (Account ID: {account_data.get("account_id")}, \n"
    This email is from Alex Bank regarding verification of your email. If you made this request, please click on the link below: \n
    https://alex-bank.com/verify.html?token={token} \n
    If you did not make such request, please ignore this email.
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


def send_contract_email(product_uid: int, email: str = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    if email is None:
        stmt = """SELECT 
                    ac.email, ac.first_name, ac.last_name, pi.contract_id, pr.name
                FROM product_instance pi
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



