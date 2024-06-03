from fastapi import APIRouter, HTTPException, Header, Depends, Request, Query
from typing import Annotated, Optional, List
from dependencies import database as db, helpers as h, schemas as s

router = APIRouter(
    prefix="/account",
    tags=["Account"]
)


@router.get("/")
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
async def get_account_info(account_no: int, emp_account_id: int,
                           token: Annotated[str | None, Header(convert_underscores=False)] = None):
    # if not db.cnx.is_connected():
    #     db.cnx, db.cursor = db.connect()
    # if not h.verify_authorization(emp_account_id, token):
    #     raise HTTPException(401, "User is not authorized")
    # if not h.check_user_privilege(emp_account_id, ['C', 'A', 'E']):
    #     raise HTTPException(401, "User does not have privileges")

    raise HTTPException(501)


@router.get("/{account_id}/verification")
async def get_info_for_verification_page(account_id: int, emp_account_id: int,
                                         token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(emp_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(emp_account_id, ['C', 'A', 'E']):
        raise HTTPException(401, "User does not have privileges")

    stmt = """
    SELECT account_id, first_name, last_name, email, phone, 
    CASE 
        WHEN country_code = 'BGR' THEN 'Bulgaria' 
        WHEN country_code = 'USA' THEN 'United States' 
        WHEN country_code = 'OTH' THEN 'Other' 
        ELSE country_code END
    AS country,
    address, verification, v.description
    FROM accounts a
    JOIN verifications v ON a.verification = v.verification_status
    WHERE a.account_id = %s"""

    db.cursor.execute(stmt, (account_id, ))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, "Account does not exist")
    row = db.cursor.fetchone()
    return {
        "account_id": int(row[0]),
        "first_name": row[1],
        "last_name":  row[2],
        "email": row[3],
        "phone": row[4],
        "country": row[5],
        "address": row[6],
        "verification_code": row[7],
        "verification": row[8],
        "verification_emoji": h.verification_emoji(row[7])
    }


@router.post("/new")
async def create_account():
    raise HTTPException(501)


@router.post("/{account_id}/verify")
async def verify_account(account_id: int, emp_account_id: int, new_verification_code: str,
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
