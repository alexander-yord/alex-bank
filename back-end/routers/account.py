from fastapi import APIRouter, HTTPException, Header, Depends, Request, Query
from typing import Annotated, Optional, List, Union
from dependencies import database as db, helpers as h, schemas as s

router = APIRouter(
    prefix="/account",
    tags=["Account"]
)


@router.get("")
def get_accounts(emp_account_id: int, country_code: Optional[List[str]] = Query(None),
                 user_role: Optional[List[str]] = Query(None), verification: Optional[List[str]] = Query(None),
                 account_group: Optional[List[str]] = Query(None),
                 token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(emp_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(emp_account_id, ['C', 'A', 'E']):
        raise HTTPException(401, "User does not have privileges")

    stmt = "SELECT a.account_id, a.first_name, a.last_name, a.email, a.phone, a.country_code, " \
           "a.address, a.user_role, ur.description, a.verification, v.description, a.account_group, " \
           "ag.group_name, ag.group_description, created_dt FROM accounts a " \
           "JOIN user_roles ur ON ur.role = a.user_role " \
           "JOIN verifications v ON v.verification_status = a.verification " \
           "JOIN account_groups ag ON ag.group_code = a.account_group"
    db.cursor.execute(stmt)
    result = [{
        "account_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "phone": row[4],
        "country_code": row[5],
        "address": row[6],
        "user_role_code": row[7],
        "user_role": row[8],
        "verification_code": row[9],
        "verification": row[10],
        "verification_emoji": h.verification_emoji(row[9]),
        "account_group_code": row[11],
        "account_group": row[12],
        "account_group_description": row[13],
        "created_dt": row[14]
    } for row in db.cursor.fetchall()]

    if account_group:  # is not empty
        result = [account for account in result if account.get("account_group_code") in account_group]
    if verification:  # is not empty
        result = [account for account in result if account.get("verification_code") in verification]
    if user_role:  # is not empty
        result = [account for account in result if account.get("user_role_code") in user_role]
    if country_code:  # is not empty
        result = [account for account in result if account.get("country_code") in country_code]

    return result


@router.get("/{account_id}")
async def get_account_info(account_id: int, usr_account_id: int,
                           token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")

    stmt = """
    SELECT a.account_id, a.first_name, a.last_name, a.email, a.phone, a.country_code, 
    CASE 
        WHEN country_code = 'BGR' THEN 'Bulgaria' 
        WHEN country_code = 'USA' THEN 'United States' 
        WHEN country_code = 'OTH' THEN 'Other' 
        ELSE country_code END
    AS country,
    a.address, a.user_role, ur.description, a.verification, v.description, a.account_group, 
    ag.group_name, ag.group_description, created_dt FROM accounts a 
    JOIN user_roles ur ON ur.role = a.user_role 
    JOIN verifications v ON v.verification_status = a.verification 
    JOIN account_groups ag ON ag.group_code = a.account_group
    WHERE a.account_id = %s"""

    db.cursor.execute(stmt, (account_id, ))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")
    row = db.cursor.fetchone()

    result = {
        "account_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "phone": row[4],
        "country_code": row[5],
        "country": row[6],
        "address": row[7],
        "user_role_code": row[8],
        "user_role": row[9],
        "verification_code": row[10],
        "verification": row[11],
        "verification_emoji": h.verification_emoji(row[10]),
        "account_group_code": row[12],
        "account_group": row[13],
        "account_group_description": row[14],
        "created_dt": row[15]
    }
    return result


@router.post("/")
async def create_account():
    raise HTTPException(501)


@router.patch("/{account_id}/verification")
async def change_account_verification_status(account_id: int, emp_account_id: int, new_verification_code: str,
                                             token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(emp_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(emp_account_id, ['C', 'A', 'E']):
        raise HTTPException(401, "User does not have privileges")

    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id, ))
    if not db.cursor.rowcount == 1:
        raise HTTPException(404, "Account not found")

    db.cursor.execute("SELECT verification_status FROM verifications WHERE verification_status = %s",
                      (new_verification_code,))
    if db.cursor.rowcount == 0:
        raise HTTPException(409, "Not a valid verification_code")

    stmt = "UPDATE accounts SET verification = %s WHERE account_id = %s"
    db.cursor.execute(stmt, (new_verification_code, account_id))
    db.cnx.commit()
    return {"status": "Success!"}


@router.patch("/{account_id}/information")
async def update_account_information(account_id: int, usr_account_id: int, data: s.AmendAccount,
                                     token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")

    if data.phone is not None:
        if len(data.phone) > 15:
            raise HTTPException(422, "Phone is too long")
        stmt = "UPDATE accounts SET phone = %s WHERE account_id = %s"
        db.cursor.execute(stmt, (data.phone, account_id))
        db.cnx.commit()

    if data.email is not None:
        if len(data.email) > 255:
            raise HTTPException(422, "Email is too long")
        stmt = "UPDATE accounts SET email = %s WHERE account_id = %s"
        db.cursor.execute(stmt, (data.email, account_id))
        db.cnx.commit()

    if data.country_code is not None:
        if data.country_code not in ['BGR', 'USA', 'OTH']:
            raise HTTPException(422, "Invalid country code")
        stmt = "UPDATE accounts SET country_code = %s WHERE account_id = %s"
        db.cursor.execute(stmt, (data.country_code, account_id))
        db.cnx.commit()

    if data.address is not None:
        stmt = "UPDATE accounts SET address = %s WHERE account_id = %s"
        db.cursor.execute(stmt, (data.address, account_id))
        db.cnx.commit()

    return {"status": "Success!"}


@router.patch("/{account_id}/group")
async def update_account_group(account_id: int, usr_account_id: int, data: s.AmendAccountGroup,
                               token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")

    db.cursor.execute("SELECT group_code FROM account_groups WHERE group_code = %s",
                      (data.account_group_code,))
    if db.cursor.rowcount == 0:
        raise HTTPException(409, "Not a valid group_code")

    stmt = "UPDATE accounts SET account_group = %s WHERE account_id = %s"
    db.cursor.execute(stmt, (data.account_group_code, account_id))
    db.cnx.commit()

    return {"status": "Success!"}


@router.patch("/{account_id}/credentials")
async def update_account_credentials(account_id: int):
    pass


@router.get("/{account_id}/products")
async def get_account_products():
    pass


@router.post("/{account_id}/product/{product_id}")
async def product_sale(account_id: int, product_id: int, usr_account_id: int, data: s.NewProduct,
                       token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")
    standard_yn = 'N' if data.standard_yn not in ['Y', 'N'] else data.standard_yn

    stmt = """
    INSERT INTO applications (account_id, product_id, standard_yn, amount_requested, special_notes, collateral)
    VALUES (%s, %s, %s, %s, %s, %s);
    """

    db.cursor.execute(stmt, (account_id, product_id, standard_yn, data.amount_requested, data.special_notes,
                             data.collateral))
    db.cnx.commit()

    db.cursor.execute("SELECT LAST_INSERT_ID()")
    application_id = db.cursor.fetchone()[0]

    stmt2 = """
    INSERT INTO product_instance (application_id, account_id, status_code)
    VALUES (%s, %s, 'APL')
    """
    db.cursor.execute(stmt2, (application_id, account_id))
    db.cnx.commit()

    db.cursor.execute("SELECT LAST_INSERT_ID()")
    product_uid = db.cursor.fetchone()[0]

    return {"status": "Success!",
            "product_uid": product_uid}


@router.get("/{account_id}/product/{product_uid}",
            response_model=Union[s.ProductInstancePrivate, s.ProductInstancePublic])
async def get_product(account_id: int, product_uid: int, usr_account_id: int,
                      token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")
    db.cursor.execute("SELECT * FROM product_instance WHERE product_uid = %s", (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} does not exist")

    stmt = """
    SELECT product_uid, is_code, status_name, status_description, update_dt FROM
    (
        SELECT 
            pi.product_uid AS product_uid, 
            ps.code AS is_code, 
            ps.status_name AS status_name, 
            ps.status_description AS status_description, 
            appl.application_dt AS update_dt
        FROM applications appl 
        JOIN product_instance pi ON pi.application_id=appl.application_id
        JOIN product_statuses ps ON ps.code='APL' 
        UNION ALL 
        SELECT 
            psu.product_uid AS product_uid, 
            psu.is_code AS is_code, 
            ps.status_name AS status_name, 
            ps.status_description AS status_description, 
            psu.update_dt AS update_dt
        FROM product_status_updates psu
        JOIN product_statuses ps ON ps.code = psu.is_code 
    ) AS status_updates
    WHERE product_uid = %s ORDER BY update_dt
    """

    db.cursor.execute(stmt, (product_uid,))
    res = db.cursor.fetchall()
    statuses = []

    for status in res:
        item = s.StatusUpdates(
            status_code=status[1],
            status_name=status[2],
            status_description=status[3],
            status_update_dt=str(status[4])
        )
        statuses.append(item)

    stmt = """
    SELECT pi.product_uid, pi.account_id, pi.status_code, ps.status_name, ps.status_description, pi.amount, 
    pi.contract_id, pi.product_start_date, pi.product_end_date, pi.actual_end_date, pi.special_notes, pi.application_id, 
    appl.approved_by, appl.amount_requested, appl.special_notes, appl.collateral, appl.approved_yn, appl.approval_dt, 
    pi.yield, pi.actual_revenue
    FROM product_instance pi 
    LEFT JOIN applications appl ON appl.application_id = pi.application_id
    JOIN product_statuses ps ON ps.code = pi.status_code
    WHERE pi.product_uid = %s
    """
    db.cursor.execute(stmt, (product_uid, ))
    res = db.cursor.fetchone()

    if h.check_user_privilege(usr_account_id, ['C', 'A', 'E']):
        prod = s.ProductInstancePrivate(
            product_uid=res[0],
            account_id=res[1],
            statuses=statuses,
            amount=res[5],
            contract_id=res[6],
            product_start_date=str(res[7]),
            product_end_date=str(res[8]),
            actual_end_date=str(res[9]),
            special_notes=res[10],
            application_id=res[11],
            approved_by=res[12],
            amount_requested=res[13],
            appl_special_notes=res[14],
            collateral=res[15],
            approved_yn=res[16],
            approval_dt=str(res[17]),
            yield_=res[18],
            actual_revenue=res[19]
        )
    else:
        prod = s.ProductInstancePublic(
            product_uid=res[0],
            account_id=res[1],
            statuses=statuses,
            amount=res[5],
            contract_id=res[6],
            product_start_date=str(res[7]),
            product_end_date=str(res[8]),
            actual_end_date=str(res[9]),
            special_notes=res[10],
            application_id=res[11],
            approved_by=res[12],
            amount_requested=res[13],
            appl_special_notes=res[14],
            collateral=res[15],
            approved_yn=res[16],
            approval_dt=str(res[17])
        )

    return prod


@router.patch("/{account_id}/product/{product_uid}/status/{new_status}")
async def update_product_status(account_id: int, product_uid: int, usr_account_id: int, new_status: str,
                                token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")
    db.cursor.execute("SELECT status_code FROM product_instance WHERE product_uid = %s", (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} does not exist")
    current_status = db.cursor.fetchone()[0]
    possible_future_statuses = h.available_next_status(current_status)
    if new_status not in possible_future_statuses.keys():
        raise HTTPException(400, f"Status {new_status} not allowed after {current_status} or does not exist")

    stmt = "UPDATE product_instance SET status_code = %s WHERE product_uid = %s"
    db.cursor.execute(stmt, (new_status, product_uid))
    db.cnx.commit()

    if new_status in ['APR', 'DEN']:
        stmt = """
        UPDATE applications SET approved_yn = %s, approved_by = %s, approval_dt = now()
        WHERE application_id = (SELECT application_id FROM product_instance WHERE product_uid = %s)
        """
        db.cursor.execute(stmt, ('Y' if current_status == 'APR' else 'N', usr_account_id, product_uid))
        db.cnx.commit()

    return {"status": "Success!"}


@router.patch("/{account_id}/product/{product_uid}")
def update_product(
        product_uid: int,
        account_id: int,
        usr_account_id: int,
        amendments: s.AmendProductInstance,
        token: Annotated[str | None, Header(convert_underscores=False)] = None
):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']):
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Account {account_id} does not exist")
    db.cursor.execute("SELECT status_code FROM product_instance WHERE product_uid = %s", (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} does not exist")

    update_fields = []
    params = []

    if amendments.amount is not None:
        update_fields.append("amount = %s")
        params.append(amendments.amount)
    if amendments.yield_ is not None:
        update_fields.append("yield = %s")
        params.append(amendments.yield_)
    if amendments.contract_id is not None:
        update_fields.append("contract_id = %s")
        params.append(amendments.contract_id)
    if amendments.expected_revenue is not None:
        update_fields.append("expected_revenue = %s")
        params.append(amendments.expected_revenue)
    if amendments.product_start_date is not None:
        update_fields.append("product_start_date = %s")
        params.append(amendments.product_start_date)
    if amendments.product_end_date is not None:
        update_fields.append("product_end_date = %s")
        params.append(amendments.product_end_date)
    if amendments.special_notes is not None:
        update_fields.append("special_notes = %s")
        params.append(amendments.special_notes)
    if amendments.actual_end_date is not None:
        update_fields.append("actual_end_date = %s")
        params.append(amendments.actual_end_date)
    if amendments.actual_revenue is not None:
        update_fields.append("actual_revenue = %s")
        params.append(amendments.actual_revenue)

    if not update_fields:
        raise HTTPException(400, "No fields to update")

    params.append(product_uid)

    stmt = f"""
    UPDATE product_instance
    SET {', '.join(update_fields)}
    WHERE product_uid = %s
    """

    db.cursor.execute(stmt, tuple(params))
    db.cnx.commit()

    return {"message": "Product updated successfully"}
