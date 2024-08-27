from fastapi import APIRouter, HTTPException
from typing import Annotated
import mysql.connector
from dependencies.database import get_db_connection
import bcrypt
from dependencies import database as db, helpers as h, schemas as s

router = APIRouter(
    prefix="/signup",
    tags=["Sign Up"]
)


@router.post("/")
async def signup(acc_info: s.NewAccount = None):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        stmt = "INSERT INTO accounts (first_name, last_name, email, phone, country_code, address, user_role, " \
               "verification, account_group) VALUES (%s, %s, %s, %s, %s, %s, 'U', 'N', 'FTC')"
        cursor.execute(stmt, (acc_info.first_name, acc_info.last_name, acc_info.email, acc_info.phone,
                              acc_info.country, acc_info.address))
        db.cnx.commit()

        stmt2 = "SELECT account_id FROM accounts WHERE first_name = %s AND last_name = %s ORDER BY 1 DESC"
        cursor.execute(stmt2, (acc_info.first_name, acc_info.last_name))
        account_id = cursor.fetchone()[0]

        # Generate a new, unique salt
        salt = bcrypt.gensalt()

        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(acc_info.password.encode('utf-8'), salt)

        stmt3 = "INSERT INTO login_credentials (account_id, password) VALUES (%s, %s)"
        cursor.execute(stmt3, (account_id, hashed_password))
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
    except mysql.connector.Error as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()