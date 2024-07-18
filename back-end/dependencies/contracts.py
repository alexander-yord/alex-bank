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
        product_custom_columns.append({
            "column_name": "Strike Date",
            "value": product_info.get("product_end_date")
        })
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

    elif product_info.get("category") == "PEQ":
        content = [
            f"This Partial Share Sale Agreement (\"Agreement\") is made and entered into as of {product_info.get('now')}, by and between {product_info.get('first_name')} {product_info.get('last_name')}, with an address {product_info.get('address')} (\"Acquirer\"), and Alex Bank (\"Seller\").",

            'RECITALS',

            f'WHEREAS, Acquirer desires to acquire issued and outstanding shares of {product_info.get("product_name")} from Seller, and Seller desires to sell such shares to Acquirer, on the terms and conditions set forth herein;',

            'NOW, THEREFORE, in consideration of the mutual covenants and promises herein contained, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the parties hereto agree as follows:',

            '1. DEFINITIONS',

            '1.1 "Acquisition" means the purchase of all of the issued and outstanding shares from Seller by Acquirer as described in this Agreement.',

            '1.2 "Closing" means the consummation of the transactions contemplated by this Agreement.',

            f'1.3 "Closing Date" means the date on which the Closing occurs, which shall be {product_info.get("product_end_date")}.',

            '1.4 "Purchase Price" means the total consideration to be paid by Acquirer for the number shares, as specified in Section 2.1.',

            '2. PURCHASE AND SALE OF SHARES',

            f'2.1 Purchase Price. The Purchase Price for the {product_info.get("yield_"):.2f}% shares of Seller shall be {product_info.get("currency")}{product_info.get("amount"):.2f}, payable, unless as otherwise specified, in cash.',

            '2.2 Payment of Purchase Price. The Purchase Price shall be paid by Acquirer to the Seller on or before the Closing Date.',

            '3. REPRESENTATIONS AND WARRANTIES',

            '3.1 Representations and Warranties of Seller. Seller represents and warrants to Acquirer as follows:',

            '(a) Organization and Good Standing. Seller is a corporation duly organized, validly existing, and in good standing, and has the corporate power and authority to own its properties and to carry on its business as now being conducted.',

            '(b) Authorization and Validity. Seller has the corporate power and authority to execute and deliver this Agreement and to perform its obligations hereunder.',

            '(c) No Conflicts. The execution, delivery, and performance of this Agreement by Seller do not and will not conflict with or result in any violation of or default under any provision of the organizational documents of Seller or any agreement or instrument to which Seller is a party.',

            '(d) Regulatory Compliance. Seller is in compliance in all material respects with all applicable laws, regulations, and rules governing its business.',

            f'(e) Financial Statements. {product_info.get("product_name")}\'s financial statements provided to Acquirer fairly present the financial condition of Seller as of the dates indicated and have been prepared in accordance with generally accepted accounting principles (GAAP) applied on a consistent basis.',

            '(f) Client Accounts. The client accounts managed by Seller are in good standing, and there are no material disputes or claims against Seller related to its client accounts.',

            '3.2 Representations and Warranties of Acquirer. Acquirer represents and warrants to Seller as follows:',

            '(a) Authorization and Validity. Acquirer has the corporate power and authority to execute and deliver this Agreement and to perform its obligations hereunder.',

            '(b) No Conflicts. The execution, delivery, and performance of this Agreement by Acquirer do not and will not conflict with or result in any violation of or default under any provision of the organizational documents of Acquirer or any agreement or instrument to which Acquirer is a party.',

            '4. COVENANTS',

            f'4.1 Conduct of Business. From the date hereof until the Closing Date, {product_info.get("product_name")} shall conduct its business in the ordinary course and shall not engage in any material transactions outside the ordinary course of business without the prior written consent of Acquirer.',

            f'4.2 Access to Information. {product_info.get("product_name")} shall allow Acquirer and its representatives reasonable access to its properties, books, and records, and shall furnish such information concerning its business as Acquirer may reasonably request.',

            '4.3 Regulatory Approvals. The parties shall use their best efforts to obtain any necessary regulatory approvals required to consummate the transactions contemplated by this Agreement.',

            '5. CONDITIONS PRECEDENT',

            '5.1 Conditions to Obligations of Acquirer. The obligations of Acquirer to consummate the transactions contemplated by this Agreement are subject to the satisfaction of the following conditions on or before the Closing Date:',

            '(a) Accuracy of Representations and Warranties. The representations and warranties of Seller contained in this Agreement shall be true and correct in all material respects as of the Closing Date.',

            '(b) Performance of Covenants. Seller shall have performed in all material respects all covenants required to be performed by it under this Agreement on or before the Closing Date.',

            '(c) Regulatory Approvals. All necessary regulatory approvals shall have been obtained.',

            '6. TERMINATION',

            '6.1 Termination. This Agreement may be terminated at any time prior to the Closing Date:',

            '(a) by mutual written consent of Acquirer and Seller;',

            '(b) by either party if the Closing shall not have occurred on or before 7 days following the Closing Date, provided that the right to terminate this Agreement under this Section 6.1(b) shall not be available to any party whose failure to fulfill any obligation under this Agreement has been the cause of or resulted in the failure of the Closing to occur on or before such date.',

            '7. MISCELLANEOUS',

            '7.1 Notices. All notices and other communications required or permitted hereunder shall be in writing and shall be deemed given if delivered through the Alex Bank CRM or via email to the email address listed officially by each party.',

            '7.2 Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the Republic of Bulgaria, without regard to its conflict of law principles.',

            '7.3 Entire Agreement. This Agreement constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior and contemporaneous agreements and understandings, both written and oral, between the parties with respect to such subject matter.',

            '7.4 Amendment. This Agreement may be amended only by a written instrument signed by both parties.',

            '7.5 Counterparts. This Agreement may be executed in one or more counterparts, each of which shall be deemed an original but all of which together shall constitute one and the same instrument.',

            f'7.6 Post-Closing Governance and Rights. Acquirer shall have the right to appoint a number of directors to the board of {product_info.get("product_name")} as directed by its Incorporating Articles, Corporate By-Laws, and other applicable rules, representing their proportional ownership of {product_info.get("yield_"):.2f}% of the outstanding shares.',

            '7.7 Sale Details' if len(product_custom_columns) > 0 else None,

            {
                "type": "table",
                "data": [[pcc["column_name"], pcc["value"]] for pcc in product_custom_columns]
            } if len(product_custom_columns) > 0 else None,

            'IN WITNESS WHEREOF, the parties hereto have caused this Agreement to be duly executed by their respective authorized officers as of the day and year first above written.',

            "Lender's Signature: Alex Bank",
            f"Date: {product_info.get('now')}",
            "Borrower's Signature: ___________________",
            "Date: _______________"
        ]
    else:
        content = [
            f"No contract can be generated.",
            "Borrower's Signature: ___________________",
            "Date: _______________"
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
