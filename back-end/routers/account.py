from fastapi import APIRouter, HTTPException, Header, Depends, Request, Query
from typing import Annotated, Optional, List
from dependencies import database as db, helpers as h, schemas as s

router = APIRouter(
    prefix="/account",
    tags=["Account"]
)


@router.get("")
def get_accounts(emp_account_id: int, country_code: Optional[List[str]] = Query(None),
                 user_role: Optional[List[str]] = Query(None), verification: Optional[List[str]] = Query(None),
                 account_group: Optional[List[str]] = Query(None),
                 token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(emp_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(emp_account_id, ['C', 'A', 'E']):
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


@router.get("/{account_id}")
async def get_account_info(account_id: int, usr_account_id: int,
                           token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
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


@router.patch("/{account_id}/verification")
async def change_account_verification_status(account_id: int, emp_account_id: int, new_verification_code: str,
                                             token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(emp_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(emp_account_id, ['C', 'A', 'E']):
        raise HTTPException(401, "User does not have privileges")

    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id, ))
    if not db.cursor.rowcount == 1:
        raise HTTPException(404, "Account not found")

    db.cursor.execute("SELECT verification_status FROM verifications WHERE verification_status = %s",
                      (new_verification_code,))
    if db.cursor.rowcount == 0:
        raise HTTPException(409, "Not a valid verification_code")

    stmt = "UPDATE accounts SET verification = %s WHERE account_id = %s"
    db.cursor.execute(stmt, (new_verification_code, account_id))
    db.cnx.commit()
    return {"status": "Success!"}


@router.patch("/{account_id}/information")
async def update_account_information(account_id: int, usr_account_id: int, data: s.AmendAccount,
                                     token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
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
async def update_account_group(account_id: int, usr_account_id: int, data: s.AmendAccountGroup,
                               token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
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


@router.patch("/{account_id}/credentials")
async def update_account_credentials(account_id: int):
    pass


@router.get("/{account_id}/products")
async def get_account_products():
    pass


@router.post("/{account_id}/product/{product_id}")
async def product_sale():
    pass


@router.get("/{account_id}/product/{product_uid}")
async def get_product():
    pass


@router.patch("/{account_id}/product/{product_uid}")
async def update_product():
    pass


