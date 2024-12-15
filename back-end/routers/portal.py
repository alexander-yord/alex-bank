from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated, Optional, List, Union
import mysql.connector
from dependencies.database import get_db_connection
from dependencies import database as db, helpers as h, schemas as s, mail as m, contracts as c
from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Query, Body, Depends

router = APIRouter(
    prefix="/portal",
    tags=["Portal"]
)


@router.get("/assigned-accounts")
async def get_assigned_accounts(token: str = Depends(s.oauth2_scheme), account_id: int = None):
    usr_account_id, usr_account_role = h.verify_token(token)
    if account_id is None:
        account_id = usr_account_id
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        if usr_account_role not in ['C', 'A', 'E']:
            raise HTTPException(401, "User does not have privileges")

        stmt = """
        SELECT 
            pi.product_uid, pi.application_id, pi.contract_id, appl.approved_by,
            p.name, p.description, NVL(pi.amount, appl.amount_requested) AS amount, 
            pi.status_code, ps.status_name, p.category_id, p.currency, 
            ac.first_name, ac.last_name, ac.account_id, nvl(p.picture_name, p.category_id)
        FROM product_instances pi
        JOIN applications appl ON appl.application_id = pi.application_id
        JOIN accounts ac ON ac.account_id = pi.account_id
        JOIN products p ON p.product_id = appl.product_id
        JOIN product_statuses ps ON ps.code = pi.status_code
        WHERE pi.product_uid in (
            select product_uid from (
                select psu.product_uid, psu.update_user, 
                       rank() over (partition by product_uid order by update_dt desc) as rnk
                from product_status_updates psu
                join accounts ac ON ac.account_id = psu.update_user and ac.user_role in ('A', 'C', 'E') 
                     and ac.account_id not in (1, 2000000)
            ) as ranked_updates
            where rnk = 1 and update_user = %s
        )
        """

        cursor.execute(stmt, (account_id,))
        rows = cursor.fetchall()
        if cursor.rowcount == 0:
            return []

        result = [s.ProductCard(
            product_uid=row[0],
            application_id=row[1],
            contract_id=row[2],
            approved_by=row[3],
            name=row[4],
            description=row[5],
            amount=row[6],
            status_code=row[7],
            status_name=row[8],
            category_id=row[9],
            currency=row[10],
            first_name=row[11],
            last_name=row[12],
            account_id=row[13],
            picture_name=row[14]
        ) for row in rows]

        return result
    except mysql.connector.Error as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.post("/validate-custom-columns")
async def verify_custom_columns(input_data: s.CustomColumnValidation):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    try:
        stmt = """select validate_custom_column(%s, %s)"""
        cursor.execute(stmt, (input_data.value, input_data.datatype))
        rows = cursor.fetchall()
        if cursor.rowcount == 0:
            return s.CustomColumnValidationResult(validation=False)
        if rows[0][0]:
            return s.CustomColumnValidationResult(validation=True)
        else:
            return s.CustomColumnValidationResult(validation=False)

    except mysql.connector.Error as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()
