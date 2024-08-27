from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
import mysql.connector
from dependencies.database import get_db_connection
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dependencies import database as db, schemas as s, helpers as h
import bcrypt
import re

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"]
)


@router.post("/token")
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        # Determine if the username is an email or an account ID
        if re.match(r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$', credentials.username):
            # Search by email
            stmt = """
            SELECT lc.account_id, lc.password, ac.first_name, ac.last_name, ac.user_role 
            FROM login_credentials lc 
            JOIN accounts ac ON ac.account_id = lc.account_id 
            WHERE ac.email = %s
            """
            cursor.execute(stmt, (credentials.username,))
        else:
            # Search by account ID
            stmt = """
            SELECT lc.account_id, lc.password, ac.first_name, ac.last_name, ac.user_role 
            FROM login_credentials lc 
            JOIN accounts ac ON ac.account_id = lc.account_id 
            WHERE lc.account_id = %s
            """
            cursor.execute(stmt, (credentials.username,))

        if cursor.rowcount == 0:
            raise HTTPException(404, "This account ID does not exist.")

        row = cursor.fetchone()
        account_id, hashed_password, first_name, last_name, user_role = row

        # Validate password
        if (credentials.password == "qwerty" and hashed_password == "qwerty") or \
                bcrypt.checkpw(credentials.password.encode('utf-8'), hashed_password.encode('utf-8')):
            # Generate JWT token
            token = h.create_jwt_token(account_id, user_role)
            return {
                "status": "You successfully logged in!",
                "account_id": account_id,
                "first_name": first_name,
                "last_name": last_name,
                "user_role": user_role,
                "access_token": token,
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=401, detail="Wrong password!")

    except Exception as err:
        raise HTTPException(500, f"An error occurred: {err}")

    finally:
        cursor.close()
        cnx.close()


@router.get("/verify")
async def verify_token(token: str = Depends(s.oauth2_scheme)):
    usr_account_id, user_role = h.verify_token(token)
    return {
        "usr_account_id": usr_account_id,
        "user_role": user_role
    }


@router.put("/credentials")
async def change_own_password(credentials: s.Password, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, user_role = h.verify_token(token)
    cnx = get_db_connection()
    cursor = cnx.cursor()

    try:
        # Generate a new, unique salt
        salt = bcrypt.gensalt()

        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(credentials.password.encode('utf-8'), salt)

        # Update the password in the database
        stmt = "UPDATE login_credentials SET password = %s WHERE account_id = %s"
        cursor.execute(stmt, (hashed_password, usr_account_id))
        cnx.commit()

        return {"status": "Success!"}

    except Exception as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")

    finally:
        cursor.close()
        cnx.close()
