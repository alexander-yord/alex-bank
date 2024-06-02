from fastapi import APIRouter, HTTPException
from typing import Annotated
from dependencies import database as db, helpers as h, schemas as s

router = APIRouter(
    prefix="/front-end",
    tags=["Front End"]
)


@router.get("/dd-options", response_model=s.DropDownOptions)  # drop-down options
async def provide_drop_down_options():
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    roles = list()
    verifications = list()
    account_groups = list()

    db.cursor.execute("SELECT role, description FROM user_roles")
    rows = db.cursor.fetchall()
    for row in rows:
        roles.append({
            "role": str(row[0]),
            "description": str(row[1])
        })

    db.cursor.execute("SELECT verification_status, description FROM verifications")
    rows = db.cursor.fetchall()
    for row in rows:
        verifications.append({
            "status_code": str(row[0]),
            "verification_status": str(row[1])
        })

    db.cursor.execute("SELECT default_YN, group_name, group_code, group_description FROM account_groups ORDER BY 1 DESC")
    rows = db.cursor.fetchall()
    for row in rows:
        account_groups.append({
            "group_name": str(row[1]),
            "group_code": str(row[2]),
            "group_description": str(row[3]),
            "default_yn": str(row[0])
        })

    return {"user_role": roles,
            "verifications": verifications,
            "account_groups": account_groups}