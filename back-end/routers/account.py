from fastapi import APIRouter, HTTPException, Header, Depends, Request
from typing import Annotated
from dependencies import database as db, helpers as h

router = APIRouter(
    prefix="/account",
    tags=["Account"]
)


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
