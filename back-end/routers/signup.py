from fastapi import APIRouter, HTTPException, Header, Depends, Request
from typing import Annotated, Dict, Set, Any
from dependencies import database as db, helpers as h, schemas as s

router = APIRouter(
    prefix="/signup",
    tags=["Sign Up"]
)


@router.post("/")
async def signup(acc_info: s.NewAccount = None) -> s.LoggedInUser:
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = "INSERT INTO accounts (first_name, last_name, email, phone, country_code, address, user_role, " \
           "verification, account_group) VALUES (%s, %s, %s, %s, %s, %s, 'U', 'N', 'FTC')"
    db.cursor.execute(stmt, (acc_info.first_name, acc_info.last_name, acc_info.email, acc_info.phone,
                             acc_info.country, acc_info.address))
    db.cnx.commit()

    stmt2 = "SELECT account_id FROM accounts WHERE first_name = %s AND last_name = %s ORDER BY 1 DESC"
    db.cursor.execute(stmt2, (acc_info.first_name, acc_info.last_name))
    account_id = db.cursor.fetchone()[0]

    stmt3 = "INSERT INTO login_credentials (account_id, password) VALUES (%s, %s)"
    db.cursor.execute(stmt3, (account_id, acc_info.password))
    db.cnx.commit()

    token = h.generate_authorization()
    stmt = "INSERT into login_sessions (account_id, token) values (%s, %s)"
    account_token_tuple = (account_id, token)
    db.cursor.execute(stmt, account_token_tuple)
    db.cnx.commit()

    result = {
        "status": "You successfully logged in!",
        "account_id": account_id,
        "first_name": acc_info.first_name,
        "last_name": acc_info.last_name,
        "user_role": 'U',
        "token": token
    }
    return result


# @router.get("/dd-options")  # drop-down options
# async def provide_drop_down_options_for_signup_page():
#     if not db.cnx.is_connected():
#         db.cnx, db.cursor = db.connect()
#     stmt = "SELECT role, description FROM user_roles"
#     db.cursor.execute(stmt)
#     rows = db.cursor.fetchall()
#
#     options = dict()
#
#     for row in rows:
#         options.update({str(row[1]): str(row[0])})
#
#     return options
