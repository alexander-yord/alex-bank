from fastapi import APIRouter, HTTPException, Header, Query, Depends
from typing import Annotated, Optional, List
import re
from dependencies import database as db, helpers as h, schemas as s, mail as m

router = APIRouter(
    prefix="/account",
    tags=["Account"]
)


@router.get("")
def get_accounts(country_code: Optional[List[str]] = Query(None),
                 user_role: Optional[List[str]] = Query(None), verification: Optional[List[str]] = Query(None),
                 account_group: Optional[List[str]] = Query(None),
                 token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E']:
        raise HTTPException(401, "User does not have privileges")

    stmt = "SELECT a.account_id, a.first_name, a.last_name, a.email, a.phone, a.country_code, " \
           "a.address, a.user_role, ur.description, a.verification, v.description, a.account_group, " \
           "ag.group_name, ag.group_description, created_dt FROM accounts a " \
           "JOIN user_roles ur ON ur.role = a.user_role " \
           "JOIN verifications v ON v.verification_status = a.verification " \
           "JOIN account_groups ag ON ag.group_code = a.account_group"
    db.cursor.execute(stmt)
    result = [{
        "account_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "phone": row[4],
        "country_code": row[5],
        "address": row[6],
        "user_role_code": row[7],
        "user_role": row[8],
        "verification_code": row[9],
        "verification": row[10],
        "verification_emoji": h.verification_emoji(row[9]),
        "account_group_code": row[11],
        "account_group": row[12],
        "account_group_description": row[13],
        "created_dt": row[14]
    } for row in db.cursor.fetchall()]

    if account_group:  # is not empty
        result = [account for account in result if account.get("account_group_code") in account_group]
    if verification:  # is not empty
        result = [account for account in result if account.get("verification_code") in verification]
    if user_role:  # is not empty
        result = [account for account in result if account.get("user_role_code") in user_role]
    if country_code:  # is not empty
        result = [account for account in result if account.get("country_code") in country_code]

    return result


@router.get("/search", response_model=List[s.AccountCard])
async def search_for_account(search_str: str, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E']:
        raise HTTPException(401, "User does not have privileges")

    # Define regular expressions
    patterns = {
        "name": r"^[a-zA-Z0-9]+$",
        "email": r"^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$",
        "group": r"^group:[A-Z]{1,3}$",
        "country_code": r"^country_code:[A-Z]{1,3}$",
        "phone": r"^phone:[+0-9]{4,15}$"
    }

    # Split the input string by whitespace
    words = search_str.split()

    # Initialize lists to hold matched words
    names = []
    email = None
    group = None
    phone = None
    country_code = None

    # Check each word against the regular expressions
    for word in words:
        if re.match(patterns["name"], word):
            names.append(word)
        elif re.match(patterns["email"], word):
            email = word
        elif re.match(patterns["group"], word):
            group = word.split(":")[1]
        elif re.match(patterns["country_code"], word):
            country_code = word.split(":")[1]
        elif re.match(patterns["phone"], word):
            phone = word.split(":")[1]

    # Construct the SQL query
    query = """
    SELECT account_id, first_name, last_name, email, phone, verification, account_group, ag.group_name
    FROM accounts ac 
    JOIN account_groups ag ON ag.group_code = ac.account_group
    WHERE """
    conditions = []
    bindings = []

    if names:
        name_str = ', '.join("'"+name+"'" for name in names)
        if len(names) == 1:
            conditions.append(f"(LOWER(first_name) IN ({name_str.lower()}) OR LOWER(last_name) IN ({name_str.lower()}))")
        else:
            conditions.append(f"(LOWER(first_name) IN ({name_str.lower()}) AND LOWER(last_name) IN ({name_str.lower()}))")
    if email:
        conditions.append(f"LOWER(email) = %s")
        bindings.append(email.lower())
    if group:
        conditions.append(f"UPPER(account_group) = %s")
        bindings.append(group.upper())
    if country_code:
        conditions.append(f"UPPER(country_code) = %s")
        bindings.append(country_code.upper())
    if phone:
        conditions.append(f"phone LIKE %s")
        bindings.append('%' + phone + '%')

    if conditions:
        query += " AND ".join(conditions)
    else:
        query += " account_id != 1"  # No conditions matched, so select all

    db.cursor.execute(query, tuple(bindings))

    if db.cursor.rowcount == 0:
        return []
    rows = db.cursor.fetchall()
    return [s.AccountCard(
        account_id=row[0],
        first_name=row[1],
        last_name=row[2],
        email=row[3],
        phone=row[4],
        verification_code=row[5],
        verification_emoji=h.verification_emoji(row[5]),
        account_group_code=row[6],
        account_group_name=row[7]
    ) for row in rows]


@router.get("/{account_id}")
async def get_account_info(account_id: int, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")

    stmt = """
    SELECT a.account_id, a.first_name, a.last_name, a.email, a.phone, a.country_code, 
    CASE 
        WHEN country_code = 'BGR' THEN 'Bulgaria' 
        WHEN country_code = 'USA' THEN 'United States' 
        WHEN country_code = 'OTH' THEN 'Other' 
        ELSE country_code END
    AS country,
    a.address, a.user_role, ur.description, a.verification, v.description, a.account_group, 
    ag.group_name, ag.group_description, created_dt FROM accounts a 
    JOIN user_roles ur ON ur.role = a.user_role 
    JOIN verifications v ON v.verification_status = a.verification 
    JOIN account_groups ag ON ag.group_code = a.account_group
    WHERE a.account_id = %s"""

    db.cursor.execute(stmt, (account_id, ))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")
    row = db.cursor.fetchone()

    result = {
        "account_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "phone": row[4],
        "country_code": row[5],
        "country": row[6],
        "address": row[7],
        "user_role_code": row[8],
        "user_role": row[9],
        "verification_code": row[10],
        "verification": row[11],
        "verification_emoji": h.verification_emoji(row[10]),
        "account_group_code": row[12],
        "account_group": row[13],
        "account_group_description": row[14],
        "created_dt": row[15]
    }
    return result


@router.post("/")
async def create_account():
    raise HTTPException(501)


@router.post("/{account_id}/send-verification-email")
async def send_verification_email(account_id: int, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E'] and not usr_account_id == account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if not db.cursor.rowcount == 1:
        raise HTTPException(404, "Account not found")
    m.send_verification_email(account_id)
    return {"message": "Success!"}


@router.post("/verify")
async def verify_account(token: str):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = "UPDATE accounts SET verification = 'Y' WHERE account_id = %s"
    db.cursor.execute(stmt, (usr_account_id,))
    db.cnx.commit()

    return {"status": "Success"}


@router.patch("/{account_id}/verification")
async def change_account_verification_status(account_id: int,  new_verification_code: str,
                                             token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E'] and \
        (new_verification_code != 'C' or account_id != usr_account_id):
        raise HTTPException(401, "User does not have privileges")

    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id, ))
    if not db.cursor.rowcount == 1:
        raise HTTPException(404, "Account not found")
    db.cursor.execute("SELECT verification_status FROM verifications WHERE verification_status = %s",
                      (new_verification_code,))
    if db.cursor.rowcount == 0:
        raise HTTPException(409, "Not a valid verification_code")

    if new_verification_code == 'C':
        m.send_verification_email(account_id)
    stmt = "UPDATE accounts SET verification = %s WHERE account_id = %s"
    db.cursor.execute(stmt, (new_verification_code, account_id))
    db.cnx.commit()
    return {"status": "Success!"}


@router.patch("/{account_id}/information")
async def update_account_information(account_id: int, data: s.AmendAccount, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")

    if data.phone is not None:
        if len(data.phone) > 15:
            raise HTTPException(422, "Phone is too long")
        stmt = "UPDATE accounts SET phone = %s WHERE account_id = %s"
        db.cursor.execute(stmt, (data.phone, account_id))
        db.cnx.commit()

    if data.email is not None:
        if len(data.email) > 255:
            raise HTTPException(422, "Email is too long")
        stmt = "UPDATE accounts SET email = %s WHERE account_id = %s"
        db.cursor.execute(stmt, (data.email, account_id))
        db.cnx.commit()

        stmt = "UPDATE accounts SET verification = 'R' WHERE account_id = %s"
        db.cursor.execute(stmt, (account_id,))
        db.cnx.commit()

    if data.country_code is not None:
        if data.country_code not in ['BGR', 'USA', 'OTH']:
            raise HTTPException(422, "Invalid country code")
        stmt = "UPDATE accounts SET country_code = %s WHERE account_id = %s"
        db.cursor.execute(stmt, (data.country_code, account_id))
        db.cnx.commit()

    if data.address is not None:
        stmt = "UPDATE accounts SET address = %s WHERE account_id = %s"
        db.cursor.execute(stmt, (data.address, account_id))
        db.cnx.commit()

    return {"status": "Success!"}


@router.patch("/{account_id}/group")
async def update_account_group(account_id: int, data: s.AmendAccountGroup, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")

    db.cursor.execute("SELECT group_code FROM account_groups WHERE group_code = %s",
                      (data.account_group_code,))
    if db.cursor.rowcount == 0:
        raise HTTPException(409, "Not a valid group_code")

    stmt = "UPDATE accounts SET account_group = %s WHERE account_id = %s"
    db.cursor.execute(stmt, (data.account_group_code, account_id))
    db.cnx.commit()

    return {"status": "Success!"}


@router.post("/{account_id}/credentials")
async def update_account_credentials(account_id: int, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E']:
        raise HTTPException(401, "User does not have privileges")

    m.send_password_reset_email(account_id)
    return {"status": "Success"}


@router.get("/{account_id}/products")
async def get_account_products(account_id: int, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")

    stmt = """
        SELECT 
            pi.product_uid, pi.application_id, pi.contract_id, appl.approved_by,
            p.name, p.description, NVL(pi.amount, appl.amount_requested) AS amount, 
            pi.status_code, ps.status_name, p.category_id, p.currency, 
            nvl(p.picture_name, p.category_id)
        FROM product_instance pi
        JOIN applications appl ON appl.application_id = pi.application_id
        JOIN products p ON p.product_id = appl.product_id
        JOIN product_statuses ps ON ps.code = pi.status_code
        WHERE pi.account_id = %s
    """

    db.cursor.execute(stmt, (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"No product found for account {account_id}.")
    rows = db.cursor.fetchall()

    result = [s.ProductCard(
        product_uid=row[0],
        application_id=row[1],
        contract_id=row[2],
        approved_by=row[3],
        name=row[4],
        description=row[5],
        amount=row[6],
        status_code=row[7],
        status_name=row[8],
        category_id=row[9],
        currency=row[10],
        picture_name=row[11]
    ) for row in rows]

    return result


@router.post("/{account_id}/product/{product_id}")
async def product_sale(account_id: int, product_id: int, data: s.NewProduct, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")
    standard_yn = 'N' if data.standard_yn not in ['Y', 'N'] else data.standard_yn

    stmt = """
    INSERT INTO applications (account_id, product_id, standard_yn, amount_requested, special_notes, collateral)
    VALUES (%s, %s, %s, %s, %s, %s);
    """

    db.cursor.execute(stmt, (account_id, product_id, standard_yn, data.amount_requested, data.special_notes,
                             data.collateral))
    db.cnx.commit()

    db.cursor.execute("SELECT LAST_INSERT_ID()")
    application_id = db.cursor.fetchone()[0]

    stmt2 = """
    INSERT INTO product_instance (application_id, account_id, status_code, latest_note)
    VALUES (%s, %s, 'APL', '')
    """
    db.cursor.execute(stmt2, (application_id, account_id))
    db.cnx.commit()

    db.cursor.execute("SELECT LAST_INSERT_ID()")
    product_uid = db.cursor.fetchone()[0]

    m.send_product_status_update_email(product_uid, 'APL')

    return {"status": "Success!",
            "product_uid": product_uid}
