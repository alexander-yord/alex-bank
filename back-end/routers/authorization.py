from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dependencies import database as db, schemas as s, helpers as h

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"]
)


@router.post("/token")
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = "SELECT lc.account_id, lc.password, ac.first_name, ac.last_name, ac.user_role FROM login_credentials lc " \
           "JOIN accounts ac ON ac.account_id = lc.account_id " \
           "WHERE lc.account_id = %s"
    db.cursor.execute(stmt, (credentials.username,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, "This account ID does not exist.")
    row = db.cursor.fetchall()[0]

    # checks if passwords match
    if credentials.password == row[1]:
        # insert a session token into the db
        account_id = int(row[0])
        token = h.create_jwt_token(account_id, row[4])

        return {
            "status": "You successfully logged in!",
            "account_id": account_id,
            "first_name": row[2],
            "last_name": row[3],
            "user_role": row[4],
            "access_token": token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(status_code=401, detail="Wrong password!")


@router.get("/verify")
async def verify_token(token: str = Depends(s.oauth2_scheme)):
    usr_account_id, user_role = h.verify_token(token)
    return {
        "usr_account_id": usr_account_id,
        "user_role": user_role
    }


# @router.put("/{account_id}/password")
# async def change_password(account_id: int, credentials: s.Password, token: Annotated[str | None, Header(convert_underscores=False)] = None):
#     if not db.cnx.is_connected():
#         db.cnx, db.cursor = db.connect()
#     if not h.verify_authorization(account_id, token):
#         raise HTTPException(401, "User is not authorized")
#
#     stmt = "UPDATE login_credentials SET password = %s WHERE account_id = %s"
#     db.cursor.execute(stmt, (credentials.password, account_id))
#     db.cnx.commit()
#
#     return {"status": "Success!"}