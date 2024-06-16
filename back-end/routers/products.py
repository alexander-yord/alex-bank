from fastapi import APIRouter, HTTPException, Header, Depends, Request, Query
from typing import Annotated, Optional, List, Union
from dependencies import database as db, helpers as h, schemas as s

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


@router.get("/products", response_model=List[s.Product])
async def list_products(category_id: Optional[str] = None, only_active_yn: str = 'Y'):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    try:
        if only_active_yn == 'N':
            sql = """
            SELECT p.product_id, p.category_id, pc.category_name, p.name, p.description, p.terms_and_conditions, 
                   p.currency, p.term, p.percentage, p.monetary_amount, p.percentage_label, p.mon_amt_label, 
                   p.available_from, p.available_till
            FROM products p
            JOIN product_categories pc ON pc.category_id = p.category_id
            WHERE 1=1
            """
        else:
            sql = """
            SELECT p.product_id, p.category_id, pc.category_name, p.name, p.description, p.terms_and_conditions, 
                   p.currency, p.term, p.percentage, p.monetary_amount, p.percentage_label, p.mon_amt_label, 
                   p.available_from, p.available_till
            FROM products p
            JOIN product_categories pc ON pc.category_id = p.category_id
            WHERE p.available_from <= NOW() AND nvl(available_till, NOW()) >= NOW()
            """

        if category_id is not None:
            sql += " AND pc.category_id = %s"
            db.cursor.execute(sql, (category_id,))
        else:
            db.cursor.execute(sql)

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
                available_till=str(prod[13].strftime('%Y-%m-%d')) if prod[13] is not None else None
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
               p.available_from, p.available_till
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
            available_till=str(product[13].strftime('%Y-%m-%d')) if product[13] is not None else None
        )

        return product_data

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/{product_id}/instances")
async def get_product_instances():
    pass


@router.get("/instances")
async def get_product_instances():
    pass


@router.get("/instance/{product_uid}",
            response_model=Union[s.ProductInstancePrivate, s.ProductInstancePublic])
async def get_product_instance(product_uid: int, usr_account_id: int,
                               token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']):
        raise HTTPException(401, "User does not have privileges")
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
    pi.yield, pi.actual_revenue, appl.product_id, pi.expected_revenue, 
    CASE WHEN appl.standard_yn = 'Y' THEN 'Standard' ELSE 'Custom' END AS standard
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
            standard=res[22]
        )
    else:
        prod = s.ProductInstancePublic(
            product_uid=res[0],
            account_id=res[1],
            statuses=statuses,
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
            product_id=res[20],
            standard=res[22]
        )

    return prod


@router.patch("/instance/{product_uid}/status/{new_status}")
async def update_product_status(product_uid: int, usr_account_id: int, new_status: str,
                                token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']):
        raise HTTPException(401, "User does not have privileges")
    db.cursor.execute("SELECT status_code FROM product_instance WHERE product_uid = %s", (product_uid,))
    if db.cursor.rowcount == 0:
        raise HTTPException(404, f"Product {product_uid} does not exist")
    current_status = db.cursor.fetchone()[0]
    possible_future_statuses = h.available_next_status(current_status)
    if not any(d["status_code"] == new_status for d in possible_future_statuses):
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


@router.patch("/instance/{product_uid}")
def update_product_instance(
        product_uid: int,
        usr_account_id: int,
        amendments: s.AmendProductInstance,
        token: Annotated[str | None, Header(convert_underscores=False)] = None
):
    print(amendments)
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(usr_account_id, token):
        raise HTTPException(401, "User is not authorized")
    if not h.check_user_privilege(usr_account_id, ['C', 'A', 'E']):
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







