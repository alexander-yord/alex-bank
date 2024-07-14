from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated, Optional, List, Union
from dependencies import database as db, helpers as h, schemas as s, mail as m, contracts as c
from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Query, Body, Depends

router = APIRouter(
    prefix="/product",
    tags=["Product"]
)


@router.get("/categories", response_model=List[s.ProductCategory])
async def get_product_categories():
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = "SELECT category_id, category_name, description FROM product_categories"
    db.cursor.execute(stmt)
    if db.cursor.rowcount == 0:
        raise HTTPException(500, "No categories found")

    rows = db.cursor.fetchall()
    category_list = []

    for row in rows:
        category_list.append(s.ProductCategory(
            category_id=row[0],
            category_name=row[1],
            category_description=row[2]
        ))
    return category_list


@router.get("/subcategories", response_model=List[s.ProductSubcategories])
async def get_product_subcategories(category_id: Optional[str] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    print (category_id)
    stmt = "SELECT subcategory_id, category_id, subcategory_name, subcategory_description FROM product_subcategories " \
           "WHERE 1=1"
    if category_id is not None:
        stmt += " AND category_id = %s"
        db.cursor.execute(stmt, (category_id,))
    else:
        db.cursor.execute(stmt)

    if db.cursor.rowcount == 0:
        return []
    rows = db.cursor.fetchall()
    return [s.ProductSubcategories(
        subcategory_id=row[0],
        category_id=row[1],
        subcategory_name=row[2],
        subcategory_description=row[3]
    ) for row in rows]


@router.get("/products", response_model=List[s.Product])
async def list_products(category_id: Optional[str] = None, subcategory_id: Optional[str] = None,
                        only_active_yn: str = 'Y'):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    try:
        sql = """
        SELECT p.product_id, p.category_id, pc.category_name, p.name, p.description, p.terms_and_conditions, 
               p.currency, p.term, p.percentage, p.monetary_amount, p.percentage_label, p.mon_amt_label, 
               p.available_from, p.available_till, nvl(p.picture_name, p.category_id), p.subcategory_id
        FROM products p
        JOIN product_categories pc ON pc.category_id = p.category_id
        WHERE 1=1
        """

        if only_active_yn == 'Y':
            sql += " AND p.available_from <= NOW() AND nvl(p.available_till, NOW()) >= NOW()"

        params = []
        if category_id is not None:
            sql += " AND p.category_id = %s"
            params.append(category_id)
        if subcategory_id is not None:
            sql += " AND p.subcategory_id = %s"
            params.append(subcategory_id)

        db.cursor.execute(sql, params)
        if db.cursor.rowcount == 0:
            return []
        products = db.cursor.fetchall()

        product_list = []
        for prod in products:
            product = s.Product(
                product_id=prod[0],
                category_id=prod[1],
                category_name=prod[2],
                name=prod[3],
                description=prod[4],
                terms_and_conditions=prod[5],
                currency=prod[6],
                term=prod[7],
                percentage=prod[8],
                monetary_amount=prod[9],
                percentage_label=prod[10],
                mon_amt_label=prod[11],
                available_from=str(prod[12].strftime('%Y-%m-%d')),
                available_till=str(prod[13].strftime('%Y-%m-%d')) if prod[13] is not None else None,
                picture_name=prod[14],
                subcategory_id=prod[15]
            )
            product_list.append(product)

        return product_list

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/{product_id}", response_model=s.Product)
async def info_about_product(product_id: int):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    try:
        sql = """
        SELECT p.product_id, p.category_id, pc.category_name, p.name, p.description, p.terms_and_conditions, 
               p.currency, p.term, p.percentage, p.monetary_amount, p.percentage_label, p.mon_amt_label, 
               p.available_from, p.available_till, nvl(p.picture_name, p.category_id)
        FROM products p
        JOIN product_categories pc ON pc.category_id = p.category_id
        WHERE p.product_id = %s
        """

        db.cursor.execute(sql, (product_id,))
        product = db.cursor.fetchone()

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        product_data = s.Product(
            product_id=product[0],
            category_id=product[1],
            category_name=product[2],
            name=product[3],
            description=product[4],
            terms_and_conditions=product[5],
            currency=product[6],
            term=product[7],
            percentage=product[8],
            monetary_amount=product[9],
            percentage_label=product[10],
            mon_amt_label=product[11],
            available_from=str(product[12].strftime('%Y-%m-%d')),
            available_till=str(product[13].strftime('%Y-%m-%d')) if product[13] is not None else None,
            picture_name=product[14]
        )

        return product_data

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/{product_id}/instances")
async def get_product_instances():
    pass


@router.get("/instances/", response_model=List[s.ProductCard])
async def get_product_instances(status_code: Optional[List[str]] = Query(None),
                                product_id: Optional[int] = None,
                                product_uid: Optional[int] = None,
                                contract_id: Optional[int] = None,
                                token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E']:
        raise HTTPException(401, "User does not have privileges")

    query = """
        SELECT 
            pi.product_uid, pi.application_id, pi.contract_id, appl.approved_by,
            p.name, p.description, NVL(pi.amount, appl.amount_requested) AS amount, 
            pi.status_code, ps.status_name, p.category_id, p.currency, 
            ac.first_name, ac.last_name, ac.account_id, nvl(p.picture_name, p.category_id)
        FROM product_instance pi
        JOIN applications appl ON appl.application_id = pi.application_id
        JOIN accounts ac ON ac.account_id = pi.account_id
        JOIN products p ON p.product_id = appl.product_id
        JOIN product_statuses ps ON ps.code = pi.status_code
        WHERE 1=1
    """

    params = []

    if product_id is not None:
        query += " AND appl.product_id = %s"
        params.append(product_id)

    if status_code is not None:
        query += " AND pi.status_code IN (%s)" % ','.join(['%s'] * len(status_code))
        params.extend(status_code)

    if product_uid is not None:
        query += " AND pi.product_uid = %s"
        params.append(product_uid)

    if contract_id is not None:
        query += " AND pi.contract_id = %s"
        params.append(contract_id)

    db.cursor.execute(query, params)
    rows = db.cursor.fetchall()

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


@router.get("/instance/{product_uid}",
            response_model=Union[s.ProductInstancePrivate, s.ProductInstancePublic])
async def get_product_instance(product_uid: int, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    db.cursor.execute("SELECT account_id FROM product_instance WHERE product_uid = %s", (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} does not exist")
    account_id = db.cursor.fetchone()[0]
    if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges")

    stmt = """
    SELECT product_uid, is_code, status_name, status_description, update_dt, update_user, ac.first_name, ac.last_name, 
    update_note, update_note_public_yn FROM
    (
        SELECT 
            pi.product_uid AS product_uid, 
            ps.code AS is_code, 
            ps.status_name AS status_name, 
            ps.status_description AS status_description, 
            appl.account_id AS update_user,
            appl.application_dt AS update_dt, 
            NULL AS update_note, 
            NULL AS update_note_public_yn
        FROM applications appl 
        JOIN product_instance pi ON pi.application_id=appl.application_id
        JOIN product_statuses ps ON ps.code='APL' 
        UNION ALL 
        SELECT 
            psu.product_uid AS product_uid, 
            psu.is_code AS is_code, 
            ps.status_name AS status_name, 
            ps.status_description AS status_description, 
            psu.update_user AS update_user,
            psu.update_dt AS update_dt, 
            psu.update_note AS update_note, 
            psu.update_note_public_yn AS update_note_public_yn
        FROM product_status_updates psu
        JOIN product_statuses ps ON ps.code = psu.is_code
    ) AS su
    LEFT JOIN accounts ac ON su.update_user = ac.account_id
    WHERE product_uid = %s ORDER BY update_dt
    """

    db.cursor.execute(stmt, (product_uid,))
    res = db.cursor.fetchall()
    statuses = []

    for status in res:
        item = s.StatusUpdates(
            status_code=status[1],  # Corresponds to ps.is_code or psu.is_code
            status_name=status[2],  # Corresponds to ps.status_name
            status_description=status[3],  # Corresponds to ps.status_description
            status_update_dt=str(status[4]),  # Corresponds to su.update_dt or psu.update_dt
            update_user=status[5] if status[5] else None,  # Corresponds to su.update_user or psu.update_user
            first_name=status[6] if status[6] else None,  # Corresponds to ac.first_name
            last_name=status[7] if status[7] else None,  # Corresponds to ac.last_name
            update_note=status[8] if status[8] and (status[9] == 'Y' or
                                                    usr_account_role in ['C', 'A', 'E']) else None,
            # Corresponds to su.update_note or psu.update_note
            public_yn=status[9] if status[9] and (status[9] == 'Y' or
                                                  usr_account_role in ['C', 'A', 'E']) else None
            # Corresponds to su.update_note_public_yn or psu.update_note_public_yn
        )

        statuses.append(item)

    stmt = """
    SELECT pccv.pcc_uid, pccv.pcc_id, pccv.product_uid, pccd.column_name, 
    pccd.customer_populatable_yn, pccd.customer_visible_yn, pccd.column_type,
    pccv.int_value, pccv.float_value, pccv.varchar_value, pccv.text_value, pccv.date_value, pccv.datetime_value
    FROM product_custom_column_values pccv 
    JOIN product_custom_column_def pccd ON pccd.pcc_id = pccv.pcc_id
    WHERE product_uid = %s
    """
    db.cursor.execute(stmt, (product_uid,))
    product_custom_columns = []
    if db.cursor.rowcount > 0:
        rows = db.cursor.fetchall()
        for row in rows:
            if usr_account_role in ['C', 'A', 'E'] or row[5] == 'Y':
                product_custom_columns.append(s.ProductCustomColumns(
                    pcc_uid=row[0],
                    pcc_id=row[1],
                    product_uid=row[2],
                    column_name=row[3],
                    customer_populatable_yn=row[4],
                    customer_visible_yn=row[5],
                    column_type=row[6],
                    int_value=row[7],
                    float_value=row[8],
                    varchar_value=row[9],
                    text_value=row[10],
                    date_value=row[11],
                    datetime_value=row[12]
                ))

    stmt = """
    SELECT pi.product_uid, pi.account_id, pi.status_code, ps.status_name, ps.status_description, pi.amount, 
    pi.contract_id, pi.product_start_date, pi.product_end_date, pi.actual_end_date, pi.special_notes, pi.application_id, 
    appl.approved_by, appl.amount_requested, appl.special_notes, appl.collateral, appl.approved_yn, appl.approval_dt, 
    pi.yield, pi.actual_revenue, appl.product_id, pi.expected_revenue, 
    CASE WHEN appl.standard_yn = 'Y' THEN 'Standard' ELSE 'Custom' END AS standard, 
    notifications_yn
    FROM product_instance pi 
    LEFT JOIN applications appl ON appl.application_id = pi.application_id
    JOIN product_statuses ps ON ps.code = pi.status_code 
    WHERE pi.product_uid = %s
    """
    db.cursor.execute(stmt, (product_uid,))
    res = db.cursor.fetchone()

    if usr_account_role in ['C', 'A', 'E']:
        prod = s.ProductInstancePrivate(
            product_uid=res[0],
            account_id=res[1],
            statuses=statuses,
            product_custom_columns=product_custom_columns,
            amount=res[5],
            contract_id=res[6],
            product_start_date=str(res[7]) if res[7] is not None else None,
            product_end_date=str(res[8]) if res[8] is not None else None,
            actual_end_date=str(res[9]) if res[9] is not None else None,
            special_notes=res[10],
            application_id=res[11],
            approved_by=res[12],
            amount_requested=res[13],
            appl_special_notes=res[14],
            collateral=res[15],
            approved_yn=res[16],
            approval_dt=str(res[17]) if res[17] is not None else None,
            yield_=res[18],
            actual_revenue=res[19],
            product_id=res[20],
            expected_revenue=res[21],
            standard=res[22],
            notifications=res[23]
        )
    else:
        prod = s.ProductInstancePublic(
            product_uid=res[0],
            account_id=res[1],
            statuses=statuses,
            product_custom_columns = product_custom_columns,
            amount=res[5],
            contract_id=res[6],
            product_start_date=str(res[7]) if res[7] is not None else None,
            product_end_date=str(res[8]) if res[8] is not None else None,
            actual_end_date=str(res[9]) if res[9] is not None else None,
            special_notes=res[10],
            application_id=res[11],
            approved_by=res[12],
            amount_requested=res[13],
            appl_special_notes=res[14],
            collateral=res[15],
            approved_yn=res[16],
            approval_dt=str(res[17]) if res[17] is not None else None,
            yield_=res[18],
            product_id=res[20],
            standard=res[22],
            notifications=res[23]
        )

    return prod


@router.patch("/instance/{product_uid}/status/{new_status}")
async def update_product_status(product_uid: int, new_status: str,
                                update_note: s.UpdateNoteModel = Body(),
                                token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E']:
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT status_code, notifications_yn FROM product_instance WHERE product_uid = %s", (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} does not exist")
    row = db.cursor.fetchone()
    current_status = row[0]
    notifications_yn = row[1]
    possible_future_statuses = h.available_next_status(current_status)
    if not any(d["status_code"] == new_status for d in possible_future_statuses):
        raise HTTPException(403, f"Status {new_status} not allowed after {current_status} or does not exist")

    if update_note.content is not None:
        stmt = "UPDATE product_instance SET " \
               "status_code = %s, latest_update_user_id = %s, latest_note = %s, latest_note_public_yn = %s " \
               "WHERE product_uid = %s"
        db.cursor.execute(stmt, (new_status, usr_account_id, update_note.content,
                                 update_note.public_yn if update_note.public_yn == 'Y' else 'N', product_uid))
    else:
        stmt = "UPDATE product_instance SET status_code = %s, latest_update_user_id = %s WHERE product_uid = %s"
        db.cursor.execute(stmt, (new_status, usr_account_id, product_uid))
    db.cnx.commit()

    if new_status in ['APR', 'DEN']:
        stmt = """
        UPDATE applications SET approved_yn = %s, approved_by = %s, approval_dt = now()
        WHERE application_id = (SELECT application_id FROM product_instance WHERE product_uid = %s)
        """
        db.cursor.execute(stmt, ('Y' if current_status == 'APR' else 'N', usr_account_id, product_uid))
        db.cnx.commit()

        if new_status == 'APR':
            c.generate_contract_string(product_uid)

    if notifications_yn == 'Y':
        m.send_product_status_update_email(product_uid, new_status)
    elif notifications_yn == 'P':
        if new_status in ["AMD", "APR", "DEN", "CNL", "SGN", "NOR", "TRG", "DUE", "ORD", "CMP"]:
            m.send_product_status_update_email(product_uid, new_status)

    return {"status": "Success!"}


@router.patch("/instance/{product_uid}/status/{new_status}/client/")
async def client_update_product_status(product_uid: int, new_status: str,
                                       update_note: s.UpdateNoteModel = Body(),
                                       token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    db.cursor.execute("SELECT status_code, account_id, notifications_yn FROM product_instance WHERE product_uid = %s",
                      (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} does not exist")
    current_status, account_id, notifications_yn = db.cursor.fetchone()
    possible_future_statuses = h.available_next_status(current_status)
    if not any(d["status_code"] == new_status for d in possible_future_statuses):
        raise HTTPException(403, f"Status {new_status} not allowed after {current_status} or does not exist")
    if new_status not in ["CNL", "AGR", "DIS"]:
        raise HTTPException(403, "This action cannot be performed by the client")

    if update_note.content is not None:
        stmt = "UPDATE product_instance SET " \
               "status_code = %s, latest_update_user_id = %s, latest_note = %s, latest_note_public_yn = %s " \
               "WHERE product_uid = %s"
        db.cursor.execute(stmt, (new_status, usr_account_id, update_note.content,
                                 update_note.public_yn if update_note.public_yn == 'Y' else 'N', product_uid))
    else:
        stmt = "UPDATE product_instance SET status_code = %s, latest_update_user_id = %s WHERE product_uid = %s"
        db.cursor.execute(stmt, (new_status, usr_account_id, product_uid))
    db.cnx.commit()

    if notifications_yn == 'Y':
        m.send_product_status_update_email(product_uid, new_status)
    elif notifications_yn == "P" and new_status == "CNL":
        m.send_product_status_update_email(product_uid, new_status)

    return {"status": "Success!"}


@router.patch("/instance/{product_uid}")
def update_product_instance(
        product_uid: int,
        amendments: s.AmendProductInstance,
        token: str = Depends(s.oauth2_scheme)
):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if usr_account_role not in ['C', 'A', 'E']:
        raise HTTPException(401, "User does not have privileges")
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


@router.post("/instance/{product_uid}/sign-contract")
async def digitally_sign_contract(product_uid: int, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    db.cursor.execute("SELECT account_id, status_code, contract_id FROM product_instance WHERE product_uid = %s",
                      (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"No product with Product UID {product_uid} found.")
    res = db.cursor.fetchone()
    if not res[0] == usr_account_id:
        raise HTTPException(401, "User is not authorized")
    if not res[1] == "SGN":
        raise HTTPException(403, "Signing not allowed for this product status.")
    db.cursor.execute("SELECT verification FROM accounts WHERE account_id = %s", (usr_account_id,))
    verification = db.cursor.fetchone()[0]
    if verification != 'Y':
        raise HTTPException(401, "Unverified accounts cannot sign a contract.")

    c.sign_contract(res[2], usr_account_id)

    stmt = "UPDATE product_instance SET status_code = 'AWT', latest_update_user_id = %s WHERE product_uid = %s"
    db.cursor.execute(stmt, (usr_account_id, product_uid))
    db.cnx.commit()

    m.send_contract_email(product_uid)

    return {"status": "Success!"}


@router.get("/instance/{product_uid}/contract/")
async def get_pdf_contract(product_uid: int, token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    db.cursor.execute("SELECT account_id, contract_id FROM product_instance WHERE product_uid = %s", (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} not found")
    res = db.cursor.fetchone()
    if usr_account_role not in ['C', 'A', 'E'] and not res[0] == usr_account_id:
        raise HTTPException(401, "User does not have privileges.")

    buffer = c.contract_buffer(res[1])

    # Create a StreamingResponse from the buffer
    return StreamingResponse(buffer, media_type='application/pdf',
                             headers={"Content-Disposition": f"attachment;filename=contract_{res[1]}.pdf"})


@router.put("/instance/{product_uid}/notifications/{new_preference}")
async def update_product_notifications_status(product_uid: int, new_preference: str,
                                              token: str = Depends(s.oauth2_scheme)):
    usr_account_id, usr_account_role = h.verify_token(token)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    db.cursor.execute("SELECT account_id FROM product_instance WHERE product_uid = %s", (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} not found")
    account_id = db.cursor.fetchone()[0]
    if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
        raise HTTPException(401, "User does not have privileges.")
    if new_preference not in ['Y', 'N', 'P']:
        raise HTTPException(403, f"{new_preference} not a valid status")

    try:
        db.cursor.execute("UPDATE product_instance SET notifications_yn = %s WHERE product_uid = %s",
                          (new_preference, product_uid))
        db.cnx.commit()
    except Exception as e:
        db.cnx.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "Success!"}


# @router.get("/instance/{product_uid}/contract/", response_class=FileResponse)
# async def download_file(product_uid: int, usr_account_id: int,
#                         token: Annotated[str | None, Header(convert_underscores=False)] = None):
#     if not db.cnx.is_connected():
#         db.cnx, db.cursor = db.connect()
#     if not h.verify_authorization(usr_account_id, token):
#         raise HTTPException(401, "User is not authorized")
#
#     try:
#         cfile = configparser.ConfigParser()
#         cfile.read(os.path.join(sys.path[0], "config.ini"))
#         UPLOAD_DIR = cfile["UPLOAD"]["UPLOAD_DIR"]
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail=str(err))
#
#     db.cursor.execute("SELECT contract_id, account_id FROM product_instance WHERE product_uid = %s", (product_uid,))
#     if db.cursor.rowcount != 1:
#         raise HTTPException(404, f"Product {product_uid} does not exist")
#     res = db.cursor.fetchone()
#     contract_id, account_id = res[0], res[1]
#
#     file_path = Path(UPLOAD_DIR) / f"upload-{contract_id}.pdf"
#
#     if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not usr_account_id == account_id:
#         raise HTTPException(401, "User does not have privileges")
#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="File not found")
#
#     return FileResponse(file_path, media_type='application/pdf', filename=f"upload-{contract_id}.pdf")
#
#
# @router.post("/instance/{product_uid}/contract")
# async def submit_signed_contract(product_uid: int, usr_account_id: int, file: UploadFile = File(...),
#                                  token: Annotated[str | None, Header(convert_underscores=False)] = None):
#     try:
#         cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
#         cfile.read(os.path.join(sys.path[0], "config.ini"))
#
#         UPLOAD_DIR = cfile["UPLOAD"]["UPLOAD_DIR"]
#         MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
#     except Exception as err:
#         print(err)
#         raise HTTPException(500, err)
#
#     if not db.cnx.is_connected():
#         db.cnx, db.cursor = db.connect()
#     if not h.verify_authorization(usr_account_id, token):
#         raise HTTPException(401, "User is not authorized")
#     # Check if the file is a PDF
#     if file.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
#     # Check if the file size is less than 10MB
#     content = await file.read()
#     if len(content) > MAX_FILE_SIZE:
#         raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
#     db.cursor.execute("SELECT account_id FROM product_instance WHERE product_uid = %s", (product_uid,))
#     if db.cursor.rowcount != 1:
#         raise HTTPException(404, f"Product {product_uid} not found.")
#     account_id = db.cursor.fetchone()[0]
#     if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']) and not usr_account_id == account_id:
#         raise HTTPException(401, "User does not have privileges")
#
#     stmt = "INSERT INTO documents (document_profile) VALUES ('CON')"
#     db.cursor.execute(stmt)
#     db.cnx.commit()
#
#     db.cursor.execute("SELECT LAST_INSERT_ID()")
#     document_id = db.cursor.fetchone()[0]
#     new_file_name = f"upload-{document_id}.pdf"
#
#     print(os.path.dirname(__file__))
#     # Save the file to the ../tmp/ folder
#     file_location = os.path.join(UPLOAD_DIR, new_file_name)
#     with open(file_location, "wb") as f:
#         f.write(content)
#
#     stmt = "UPDATE documents SET document_name = %s WHERE document_id = %s"
#     db.cursor.execute(stmt, (new_file_name, document_id))
#     db.cnx.commit()
#
#     stmt = "UPDATE product_instance SET contract_id = 1 WHERE product_uid = %s"
#     db.cursor.execute(stmt, (product_uid,))
#     db.cnx.commit()
#
#     return {"filename": new_file_name}
