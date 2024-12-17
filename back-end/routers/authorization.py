from fastapi import APIRouter, HTTPException, Depends
import pyotp
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
        if re.match(r'^[A-Za-z0-9-_]+?\.[A-Za-z0-9-_]+?\.[A-Za-z0-9-_]+$', credentials.username):
            # if the username field is a JWT stage token, then:
            account_id, requires_2fa = h.verify_stage_token(credentials.username)

            if requires_2fa:
                stmt = """
                SELECT otp_key FROM login_credentials WHERE account_id = %s
                """
                cursor.execute(stmt, (account_id,))
                rows = cursor.fetchall()
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="No OTP code found for this account")
                otp_key = rows[0][0]

                totp = pyotp.TOTP(otp_key)
                if totp.verify(credentials.password):
                    return h.login(account_id)
                else:
                    raise HTTPException(status_code=401, detail="Incorrect OTP code")

        else:  # i.e., if the username field is not a JWT token, then:

            # check if the username is an email
            if re.match(r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$', credentials.username):
                # Search by email
                stmt = """
                SELECT lc.account_id, lc.password, lc.otp_key, ac.verification
                FROM login_credentials lc
                JOIN accounts ac ON ac.account_id = lc.account_id
                WHERE ac.email = %s
                """
                cursor.execute(stmt, (credentials.username,))
            else:
                # Search by account ID
                stmt = """
                SELECT lc.account_id, lc.password, lc.otp_key, ac.verification
                FROM login_credentials lc
                JOIN accounts ac ON ac.account_id = lc.account_id
                WHERE lc.account_id = %s
                """
                cursor.execute(stmt, (credentials.username,))

            rows = cursor.fetchall()
            if cursor.rowcount == 0:
                raise HTTPException(404, "This account ID does not exist.")

            account_id, hashed_password, otp_key, verification = rows[0]

            # Validate password
            if (credentials.password == "qwerty" and hashed_password == "qwerty") or \
                    bcrypt.checkpw(credentials.password.encode('utf-8'), hashed_password.encode('utf-8')):
                if verification == "Y":
                    auth_stage_token = h.create_jwt_stage_token(account_id)
                    return {
                        "requires_2fa": True,
                        "auth_stage_token": auth_stage_token
                    }
                else:
                    return h.login(account_id)
            else:
                raise HTTPException(status_code=401, detail="Wrong password!")

    except mysql.connector.Error as err:
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
