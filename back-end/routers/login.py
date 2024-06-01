from fastapi import APIRouter, HTTPException
from dependencies import database as db, schemas as s, helpers as h

router = APIRouter(
    prefix="/login",
    tags=["Log In"]
)


@router.post("/{account_id}")
async def login(account_id: int, credentials: s.Password) -> s.LoggedInUser:
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = "SELECT lc.account_id, lc.password, ac.first_name, ac.last_name, ac.user_role FROM login_credentials lc " \
           "JOIN accounts ac ON ac.account_id = lc.account_id " \
           "WHERE lc.account_id = %s"

    id_tuple = (account_id,)
    db.cursor.execute(stmt, id_tuple)
    if db.cursor.rowcount == 0:
        raise HTTPException(404, "This account ID does not exist.")
    row = db.cursor.fetchall()[0]

    # checks if passwords match
    if credentials.password == row[1]:
        # insert a session token into the db
        account_id = int(row[0])
        token = h.generate_authorization()
        stmt = "INSERT into login_sessions (account_id, token) values (%s, %s)"
        account_token_tuple = (account_id, token)
        db.cursor.execute(stmt, account_token_tuple)
        db.cnx.commit()

        result = {
            "status": "You successfully logged in!",
            "account_id": account_id,
            "first_name": row[2],
            "last_name": row[3],
            "user_role": row[4],
            "token": token
        }
        return result
    else:
        raise HTTPException(status_code=401, detail="Wrong password!")

