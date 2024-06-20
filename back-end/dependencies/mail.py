from . import database as db, helpers as h
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

        smtp_server = 'smtp.gmail.com'
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
    msg['From'] = smtp_user
    msg['To'] = account_data.get("email")
    msg['Subject'] = f"{account_data.get('first_name')} - Verify Your Email"

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
        print('Email sent successfully.')
    except Exception as e:
        print(f'Failed to send email: {e}')


def create_loan_contract(product_uid: int):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    buffer = io.BytesIO()
    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()

    stmt = """
    SELECT DATE_FORMAT(NOW(), '%M %d, %Y') as now,  pi.amount, pi.yield, pr.currency,
        DATE_FORMAT(pi.product_start_date, '%M %d, %Y') as product_begin_date, 
        DATE_FORMAT(pi.product_end_date, '%M %d, %Y') as product_end_date,
        ac.first_name, ac.last_name, ac.address, ac.country_code, 
        CASE WHEN ac.country_code = 'BGR' THEN 'Bulgaria'
        WHEN ac.country_code = 'USA' THEN 'United States'
        ELSE 'OTH' END AS country 
    FROM product_instance pi 
    JOIN accounts ac ON ac.account_id = pi.account_id
    JOIN applications appl ON appl.application_id = pi.application_id
    JOIN products pr ON appl.product_id = pr.product_id
    WHERE pi.product_uid = %s
    """
    db.cursor.execute(stmt, (product_uid, ))
    res = db.cursor.fetchone()

    address = ""
    if res[10] == "OTH":
        if res[8] != "" and res[8] is not None:
            address = res[8]
        else:
            address = "Not Specified"
    else:
        if res[8] != "" and res[8] is not None:
            address = res[9] + ", " + res[10]

    product_info = {
        "now": res[0],
        "amount": res[1],
        "yield_": float(res[2])*100,
        "currency": res[3],
        "product_begin_date": res[4],
        "product_end_date": res[5],
        "first_name": res[6],
        "last_name": res[7],
        "address": address
    }

    # Contract content
    content = [
        f"This Loan Contract Agreement (the 'Agreement') is made and entered into as of {product_info.get('now')}, "
        f"by and between Alex Bank ('Lender') and {product_info.get('first_name')} {product_info.get('last_name')}, "
        f"with an address {product_info.get('address')} ('Borrower').",

        f"1. Loan Amount: The Lender agrees to loan the Borrower the amount of {product_info.get('currency')}"
        f"{product_info.get('amount'):.2f} (the 'Principal').",

        f"2. Repayment Terms: The Borrower agrees to repay the Loan Amount with interest at a rate of "
        f"{product_info.get('yield_'):.2f}% per each month of the duration of the contract, beginning on "
        f"{product_info.get('product_begin_date')} and ending on {product_info.get('product_end_date')}. "
        f"The Loan (its Principal, accrued interest, and fees) shall be repayed in full on "
        f"{product_info.get('product_end_date')}.",

        "3. Late Payment: If the repayment is not received by the Lender within 5 business days of the due date, "
        "the Borrower shall pay a late fee of 0.5% of the overdue amount (the Principal + interest + fees) for "
        "each day the amount is not paid after the first week after the due date. ",

        "4. Prepayment: The Borrower may prepay the Loan in full (its principal amount and the pro rata interest) "
        "at any time without penalty. ",

        "5. Default: The Loan shall be considered in default if the Borrower fails to make the payment one month after "
        "the due date, "
        "or if the Borrower breaches any other terms of this Agreement. In the event of default, the Lender may demand "
        "immediate repayment of the entire outstanding Loan amount, including accrued interest and fees.",

        "6. Entire Agreement: This Agreement constitutes the entire agreement between the parties and supersedes "
        "all prior understandings, agreements, representations, and warranties, both written and oral, with respect to "
        "the subject matter hereof.",

        "IN WITNESS WHEREOF, the parties hereto have executed this Loan Contract Agreement as of the day and "
        "year first above written.",
    ]

    # Create a list to hold the flowable elements
    flowables = []

    # Add image in the upper left corner
    image = Image("alex_bank.png")  # Replace with the actual path to your image
    image.drawHeight = 1.25 * inch * image.drawHeight / image.drawWidth
    image.drawWidth = 1.25 * inch
    flowables.append(image)
    flowables.append(Spacer(1, 24))

    # Title
    title = Paragraph("Loan Contract Agreement", styles['Title'])
    flowables.append(title)
    flowables.append(Spacer(1, 24))

    # Add content paragraphs
    for line in content:
        paragraph = Paragraph(line, styles['Normal'])
        flowables.append(paragraph)
        flowables.append(Spacer(1, 12))

    # Signature area
    signature_lines = [
        "Lender's Signature: ______________________",
        "Date: _______________",
        "Borrower's Signature: ___________________",
        "Date: _______________",
    ]

    for line in signature_lines:
        paragraph = Paragraph(line, styles['Normal'])
        flowables.append(Spacer(1, 24))
        flowables.append(paragraph)

    # Build the PDF
    doc.build(flowables)
    buffer.seek(0)
    return buffer


def send_contract_email(product_uid: int, email: str = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    if email is None:
        db.cursor.execute("SELECT ac.email FROM product_instance pi JOIN accounts ac ON ac.account_id = pi.account_id "
                          "WHERE pi.product_uid = %s", (product_uid,))
        email = db.cursor.fetchone()[0]

    try:
        cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
        cfile.read(os.path.join(sys.path[0], "config.ini"))

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_user = cfile["SMTP"]["MAIL_USER"]
        smtp_password = cfile["SMTP"]["MAIL_PASS"]

    except Exception as err:
        print(err)
        return ;

    # Email content
    from_email = 'smpt.alex.bank.com@gmail.com'
    to_email = email
    subject = 'Test Email with PDF Contract Attachment'
    body = 'This is a test email sent from Python with a PDF attachment.'

    # Create the email message
    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    # Create PDF and attach it to the email
    pdf_buffer = create_loan_contract(product_uid)
    pdf_name = 'loan_contract.pdf'
    msg.add_attachment(pdf_buffer.read(), maintype='application', subtype='pdf', filename=pdf_name)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print('Email sent successfully.')
    except Exception as e:
        print(f'Failed to send email: {e}')


