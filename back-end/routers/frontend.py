from fastapi import APIRouter, HTTPException
from typing import Annotated
import mysql.connector
from dependencies.database import get_db_connection
from dependencies import database as db, helpers as h, schemas as s

router = APIRouter(
    prefix="/front-end",
    tags=["Front End"]
)


@router.get("/dd-options", response_model=s.DropDownOptions)  # drop-down options
async def provide_drop_down_options():
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        roles = list()
        verifications = list()
        account_groups = list()
        statuses = list()

        cursor.execute("SELECT role, description FROM user_roles")
        rows = cursor.fetchall()
        for row in rows:
            roles.append({
                "role": str(row[0]),
                "description": str(row[1])
            })

        cursor.execute("SELECT verification_status, description FROM verifications")
        rows = cursor.fetchall()
        for row in rows:
            verifications.append({
                "status_code": str(row[0]),
                "verification_status": str(row[1])
            })

        cursor.execute("SELECT default_YN, group_name, group_code, group_description FROM account_groups ORDER BY 1 DESC")
        rows = cursor.fetchall()
        for row in rows:
            account_groups.append({
                "group_name": str(row[1]),
                "group_code": str(row[2]),
                "group_description": str(row[3]),
                "default_yn": str(row[0])
            })

        cursor.execute("SELECT code, status_name, call_to_action, status_description FROM product_statuses "
                       "ORDER BY order_no")
        rows = cursor.fetchall()
        for row in rows:
            statuses.append(s.Statuses(
                status_code=row[0],
                status_name=row[1],
                call_to_action=row[2],
                status_description=row[3],
                show=True
            ))

        return {"user_role": roles,
                "verifications": verifications,
                "account_groups": account_groups,
                "statuses": statuses}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        cnx.close()


@router.get("/statuses")
async def provide_available_product_statuses(current_status: str):
    res = h.available_next_status(current_status)
    if res == "XXX":
        raise HTTPException(404, f"Status code {current_status} does not exist")
    return res


@router.get("/status-progression")
async def provide_status_progression(current_status: str):
    res = h.status_progressions(current_status)
    if res == "XXX":
        raise HTTPException(404, f"Status code {current_status} does not exist")
    return res
