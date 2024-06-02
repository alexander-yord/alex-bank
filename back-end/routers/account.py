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

    stmt = "SELECT account_id, first_name, last_name, email, phone, country_code, " \
           "address, user_role, verification, account_group FROM accounts"
    db.cursor.execute(stmt)
    result = [{
        "account_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "phone": row[4],
        "country_code": row[5],
        "address": row[6],
        "user_role": row[7],
        "verification": row[8],
        "account_group": row[9]
    } for row in db.cursor.fetchall()]

    if account_group:  # is not empty
        result = [account for account in result if account.get("account_group") in account_group]
    if verification:  # is not empty
        result = [account for account in result if account.get("verification") in verification]
    if user_role:  # is not empty
        result = [account for account in result if account.get("user_role") in user_role]
    if country_code:  # is not empty
        result = [account for account in result if account.get("country_code") in country_code]

    return result


@router.get("/{account_id}")
async def get_account_info(account_no: int, token: Annotated[str | None, Header(convert_underscores=False)] = None):
    raise HTTPException(501)


@router.post("/new")
async def create_account():
    raise HTTPException(501)


@router.post("/{account_id}/verify")
async def verify_account(account_id: int, emp_account_id: int,
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

    stmt = "UPDATE accounts SET verification = 'Y' WHERE account_id = %s"
    db.cursor.execute(stmt, (account_id, ))
    db.cnx.commit()
    return {"status": "Success!"}
