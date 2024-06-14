from fastapi import APIRouter, HTTPException, Header, Depends, Request, Query
from typing import Annotated, Optional, List
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


@router.get("/instance")
async def get_product_instance():
    pass






