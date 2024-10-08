from fastapi import APIRouter, HTTPException
from typing import Annotated
import bcrypt
from dependencies import database as db, helpers as h, schemas as s

router = APIRouter(
    prefix="/signup",
    tags=["Sign Up"]
)


@router.post("/")
async def signup(acc_info: s.NewAccount = None):
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

    # Generate a new, unique salt
    salt = bcrypt.gensalt()

    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(acc_info.password.encode('utf-8'), salt)

    stmt3 = "INSERT INTO login_credentials (account_id, password) VALUES (%s, %s)"
    db.cursor.execute(stmt3, (account_id, hashed_password))
    db.cnx.commit()

    token = h.create_jwt_token(account_id, 'U')

    return {
        "status": "You successfully logged in!",
        "account_id": account_id,
        "first_name": acc_info.first_name,
        "last_name": acc_info.last_name,
        "user_role": 'U',
        "access_token": token,
        "token_type": "bearer"
    }
