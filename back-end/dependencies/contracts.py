from . import database as db
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
import json


def generate_contract_string(product_uid: int):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = """
        SELECT DATE_FORMAT(NOW(), '%M %d, %Y') as now,  pi.amount, pi.yield, pr.currency,
            DATE_FORMAT(pi.product_start_date, '%M %d, %Y') as product_begin_date, 
            DATE_FORMAT(pi.product_end_date, '%M %d, %Y') as product_end_date,
            ac.first_name, ac.last_name, ac.address, ac.country_code, 
            CASE WHEN ac.country_code = 'BGR' THEN 'Bulgaria'
            WHEN ac.country_code = 'USA' THEN 'United States'
            ELSE 'OTH' END AS country, 
            pr.category_id, pr.name, pr.description
        FROM product_instance pi 
        JOIN accounts ac ON ac.account_id = pi.account_id
        JOIN applications appl ON appl.application_id = pi.application_id
        JOIN products pr ON appl.product_id = pr.product_id
        WHERE pi.product_uid = %s
        """
    db.cursor.execute(stmt, (product_uid,))
    try:
        res = db.cursor.fetchone()
    except Exception as err:
        return err

    address = ""
    if res[10] == "OTH":
        if res[8] != "" and res[8] is not None:
            address = res[8]
        else:
            address = "Not Specified"
    else:
        if res[8] != "" and res[8] is not None:
            address = res[8] + ", " + res[10]
        else:
            address = "in " + res[10]

    product_info = {
        "now": res[0],
        "amount": res[1],
        "yield_": float(res[2]) * 100,
        "currency": res[3],
        "product_begin_date": res[4],
        "product_end_date": res[5],
        "first_name": res[6],
        "last_name": res[7],
        "address": address,
        "category": res[11],
        "product_name": res[12],
        "product_description": res[13]
    }

    stmt = """
    SELECT pccv.pcc_uid, pccv.pcc_id, pccv.product_uid, pccd.column_name, 
    pccd.customer_populatable_yn, pccd.customer_visible_yn, pccd.column_type,
    pccv.int_value, pccv.float_value, pccv.varchar_value, pccv.text_value, pccv.date_value, pccv.datetime_value
    FROM product_custom_column_values pccv 
    JOIN product_custom_column_def pccd ON pccd.pcc_id = pccv.pcc_id
    WHERE product_uid = %s AND pccd.customer_visible_yn = 'Y'
    """
    db.cursor.execute(stmt, (product_uid,))

    product_custom_columns = []
    if db.cursor.rowcount != 0:
        rows = db.cursor.fetchall()
        for row in rows:
            if row[6] == "integer":
                value = row[7]
            elif row[6] == "float":
                value = row[8]
            elif row[6] == "char" or row[6] == "varchar":
                value = row[9]
            elif row[6] == "text":
                value = row[10]
            elif row[6] == "date":
                value = row[11].strftime('%B %d, %Y') if row[11] else None
            elif row[6] == "datetime":
                value = row[12].strftime('%B %d, %Y %H:%M:%S') if row[12] else None
            else:
                value = None
            product_custom_columns.append({
                "column_name": row[3],
                "value": value
            })

    # Contract content
    if product_info["category"] == 'LON':
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

            "5. Default: The Loan shall be considered in default if the Borrower fails to make the payment one month "
            "after the due date, or if the Borrower breaches any other terms of this Agreement. In the event of "
            "default, the Lender may demand immediate repayment of the entire outstanding Loan amount, including "
            "accrued interest and fees.",

            "6. Entire Agreement: This Agreement constitutes the entire agreement between the parties and supersedes "
            "all prior understandings, agreements, representations, and warranties, both written and oral, with respect"
            " to the subject matter hereof.",

            f"Product UID: {product_uid}",

            "IN WITNESS WHEREOF, the parties hereto have executed this Loan Contract Agreement as of the day and "
            "year first above written.",

            "Lender's Signature: Alex Bank",
            f"Date: {product_info.get('now')}",
            "Borrower's Signature: ___________________",
            "Date: _______________"
        ]
    elif product_info["category"] == "DER":
        content = [
            f"This {product_info.get('product_name')} Contract Agreement (the 'Agreement') is made and entered into as of {product_info.get('now')}, by and between Alex Bank ('Issuer') and {product_info.get('first_name')} {product_info.get('last_name')}, with an address {product_info.get('address')} ('Holder').",
            f"The Holder agrees to buy this product with Product UID {product_info.get('product_uid')} from the Issuer on the Product Begin Date ({product_info.get('product_begin_date')}).",
            f"If a Product UID is linked to this Product, the owner of that Product shall be deemed the counterparty to this Product. Alex Bank shall act as an intermediary between the two parties but shall not assume liability for the fulfillment of any party's financial obligations. In consideration of its intermediary services, Alex Bank shall receive a commission, as detailed below.",
            f"This {product_info.get('product_name')} shall be characterized by the following rule: {product_info.get('product_description')}. This may be altered, augmented, or superseded by any rule hereinafter delineated."
            f"Unless as otherwise specified, the Issuer, or the substituting counterpatry, agrees that on the Product End Date ({product_info.get('product_end_date')}) and on any of the listed observation/exercise dates, if the option condition is met, the option may be exercised.",
            {
                "type": "table",
                "data": [[pcc["column_name"], pcc["value"]] for pcc in product_custom_columns]
            } if len(product_custom_columns) > 0 else None,
            "IN WITNESS WHEREOF, the parties hereto have executed this Loan Contract Agreement as of the day and year first above written.",

            "Lender's Signature: Alex Bank",
            f"Date: {product_info.get('now')}",
            "Borrower's Signature: ___________________",
            "Date: _______________"
        ]
    else:
        content = [
            f"No contract can be generated."
        ]

    json_string = json.dumps(content)
    db.cursor.execute("INSERT INTO contracts (unsigned_contract) VALUES (%s)", (json_string,))
    db.cnx.commit()

    db.cursor.execute("SELECT LAST_INSERT_ID()")
    contract_id = db.cursor.fetchone()[0]

    db.cursor.execute("UPDATE product_instance SET contract_id = %s WHERE product_uid = %s", (contract_id, product_uid))
    db.cnx.commit()
    return


def sign_contract(contract_id: int, account_id: int):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    db.cursor.execute("SELECT unsigned_contract, DATE_FORMAT(NOW(), '%M %d, %Y') FROM contracts WHERE contract_id = %s",
                      (contract_id,))
    if db.cursor.rowcount == 0:
        return
    unsigned_contract, now = db.cursor.fetchone()
    contents = json.loads(unsigned_contract)

    db.cursor.execute("SELECT first_name, last_name FROM accounts where account_id = %s", (account_id,))
    first_name, last_name = db.cursor.fetchone()

    contents[-2] = f"Borrower's Signature: {first_name} {last_name} [digitally signed]"
    contents[-1] = f"Date: {now}"

    signed_contract = json.dumps(contents)
    db.cursor.execute("UPDATE contracts SET signed_contract = %s WHERE contract_id = %s", (signed_contract, contract_id))
    db.cnx.commit()
    return


def contract_buffer(contract_id: int, unsigned: bool = False):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    buffer = io.BytesIO()
    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()

    if unsigned:
        stmt = "SELECT unsigned_contract FROM contracts WHERE contract_id = %s"
    else:
        stmt = "SELECT nvl(signed_contract, unsigned_contract) FROM contracts WHERE contract_id = %s"
    db.cursor.execute(stmt, (contract_id,))
    res = db.cursor.fetchone()
    if res is None:
        print(f"No contract found for contract_id: {contract_id}")
        return None

    content = json.loads(res[0])

    # Create a list to hold the flowable elements
    flowables = []

    # Add image in the upper left corner
    image = Image("alex_bank.png")  # Replace with the actual path to your image
    image.drawHeight = 1.25 * inch * image.drawHeight / image.drawWidth
    image.drawWidth = 1.25 * inch
    flowables.append(image)
    flowables.append(Spacer(1, 24))

    # Title
    title = Paragraph("Alex Bank Contract Agreement", styles['Title'])
    flowables.append(title)
    flowables.append(Spacer(1, 24))

    # Add content paragraphs and tables
    for item in content:
        if isinstance(item, str):
            # It's a paragraph
            paragraph = Paragraph(item, styles['Normal'])
            flowables.append(paragraph)
            flowables.append(Spacer(1, 12))
        elif isinstance(item, dict) and item.get("type") == "table":
            # It's a table
            data = item.get("data", [])
            table = Table(data)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            flowables.append(table)
            flowables.append(Spacer(1, 24))

    # Build the PDF
    doc.build(flowables)
    buffer.seek(0)
    return buffer
