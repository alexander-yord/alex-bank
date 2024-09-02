from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated, Optional, List, Union
import random, string
import mysql.connector
from dependencies import helpers as h, schemas as s, mail as m, contracts as c
from dependencies.database import get_db_connection
from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Query, Body, Depends

router = APIRouter(
    prefix="/product",
    tags=["Product"]
)


@router.get("/categories", response_model=List[s.ProductCategory])
async def get_product_categories(only_catalog_yn: Optional[str] = 'Y'):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        stmt = "SELECT category_id, category_name, description, catalog_yn, term_label, percentage_label, " \
               "mon_amt_label FROM product_categories "
        if only_catalog_yn != 'N':
            stmt += "WHERE catalog_yn = 'Y'"

        cursor.execute(stmt)
        rows = cursor.fetchall()

        if cursor.rowcount == 0:
            raise HTTPException(404, "No categories found")

        category_list = []

        for row in rows:
            category_list.append(s.ProductCategory(
                category_id=row[0],
                category_name=row[1],
                category_description=row[2],
                catalog_yn=row[3],
                term_label=row[4],
                percentage_label=row[5],
                mon_amt_label=row[6]
            ))
        return category_list

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))

    finally:
        cursor.close()
        cnx.close()


@router.post("/category", response_model=s.ProductCategory)
async def create_new_category(category_info: s.ProductCategory, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A']:
            raise HTTPException(401, "User does not have privileges")

        code = category_info.category_id[:3]
        while True:
            cursor.execute("SELECT count(*) FROM product_categories WHERE category_id = %s", (code,))
            if cursor.fetchone()[0] == 0:
                break
            code = code[0] + ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))

        stmt = """
            INSERT INTO product_categories (
                category_id, category_name, description, catalog_yn, 
                term_label, percentage_label, mon_amt_label
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(stmt, (
            code,
            category_info.category_name,
            category_info.category_description,
            category_info.catalog_yn if category_info.catalog_yn == "Y" else "N",
            category_info.term_label,
            category_info.percentage_label,
            category_info.mon_amt_label
        ))
        cnx.commit()

        return s.ProductCategory(
            category_id=code,
            category_name=category_info.category_name,
            category_description=category_info.category_description,
            catalog_yn=category_info.catalog_yn if category_info.catalog_yn == "Y" else "N",
            term_label=category_info.term_label,
            percentage_label=category_info.percentage_label,
            mon_amt_label=category_info.mon_amt_label
        )

    except mysql.connector.Error as err:
        raise HTTPException(500, str(err))

    finally:
        cursor.close()
        cnx.close()


@router.patch("/category/{category_id}")
async def update_category(category_id: str, category_info: s.AmendProductCategory, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A']:
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT category_id FROM product_categories WHERE category_id = %s", (category_id,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product category {category_id} not found.")

        # Prepare the update statement dynamically based on provided fields
        update_fields = []
        update_values = []

        if category_info.category_name is not None:
            update_fields.append("category_name = %s")
            update_values.append(category_info.category_name)

        if category_info.category_description is not None:
            update_fields.append("description = %s")
            update_values.append(category_info.category_description)

        if category_info.catalog_yn is not None:
            update_fields.append("catalog_yn = %s")
            update_values.append('Y' if category_info.catalog_yn == 'Y' else 'N')

        if category_info.term_label is not None:
            update_fields.append("term_label = %s")
            update_values.append(category_info.term_label)

        if category_info.percentage_label is not None:
            update_fields.append("percentage_label = %s")
            update_values.append(category_info.percentage_label)

        if category_info.mon_amt_label is not None:
            update_fields.append("mon_amt_label = %s")
            update_values.append(category_info.mon_amt_label)

        if update_fields:
            update_values.append(category_id)
            stmt = f"UPDATE product_categories SET {', '.join(update_fields)} WHERE category_id = %s"
            cursor.execute(stmt, tuple(update_values))
            cnx.commit()

        return {"status": "Success!"}

    except mysql.connector.Error as err:
        raise HTTPException(500, str(err))

    finally:
        cursor.close()
        cnx.close()


@router.get("/subcategories", response_model=List[s.ProductSubcategories])
async def get_product_subcategories(category_id: Optional[str] = None, only_catalog_yn: Optional[str] = 'Y'):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        stmt = """
            SELECT DISTINCT 
                ps.subcategory_id, 
                ps.category_id, 
                ps.subcategory_name, 
                ps.subcategory_description, 
                ps.catalog_yn, 
                count(product_id) OVER (PARTITION BY ps.subcategory_id) as row_cnt,
                ps.term_label,        
                ps.percentage_label,  
                ps.mon_amt_label   
            FROM product_subcategories ps 
            LEFT JOIN products p ON p.subcategory_id = ps.subcategory_id 
            WHERE 1=1
        """
        params = []
        if category_id is not None:
            stmt += " AND ps.category_id = %s"
            params.append(category_id)
        if only_catalog_yn != "N":
            stmt += " AND ps.catalog_yn = 'Y'"

        cursor.execute(stmt, tuple(params))
        rows = cursor.fetchall()

        if not rows:
            return []

        return [
            s.ProductSubcategories(
                subcategory_id=row[0],
                category_id=row[1],
                subcategory_name=row[2],
                subcategory_description=row[3],
                catalog_yn=row[4],
                product_count=row[5],
                term_label=row[6],
                percentage_label=row[7],
                mon_amt_label=row[8]
            ) for row in rows
        ]

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))

    finally:
        cursor.close()
        cnx.close()


@router.post("/subcategory", response_model=s.ProductSubcategories)
async def create_new_subcategory(subcategory_info: s.NewProductSubcategory, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A']:
            raise HTTPException(status_code=401, detail="User does not have privileges")

        cursor.execute("SELECT category_id FROM product_categories WHERE category_id = %s", (subcategory_info.category_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail=f"Product category {subcategory_info.category_id} not found.")

        stmt = """
            INSERT INTO product_subcategories (
                category_id, 
                subcategory_name, 
                subcategory_description, 
                catalog_yn, 
                term_label, 
                percentage_label, 
                mon_amt_label
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(stmt, (
            subcategory_info.category_id,
            subcategory_info.subcategory_name,
            subcategory_info.subcategory_description,
            "Y" if subcategory_info.catalog_yn == 'Y' else 'N',
            subcategory_info.term_label,
            subcategory_info.percentage_label,
            subcategory_info.mon_amt_label
        ))
        cnx.commit()

        cursor.execute("SELECT LAST_INSERT_ID()")
        subcategory_id = cursor.fetchone()[0]

        return s.ProductSubcategories(
            subcategory_id=subcategory_id,
            category_id=subcategory_info.category_id,
            subcategory_name=subcategory_info.subcategory_name,
            subcategory_description=subcategory_info.subcategory_description,
            catalog_yn="Y" if subcategory_info.catalog_yn == 'Y' else 'N',
            term_label=subcategory_info.term_label,
            percentage_label=subcategory_info.percentage_label,
            mon_amt_label=subcategory_info.mon_amt_label
        )

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))

    finally:
        cursor.close()
        cnx.close()


@router.patch("/subcategory/{subcategory_id}", response_model=s.ProductSubcategories)
async def modify_subcategory(subcategory_id: int, subcategory_info: s.AmendProductSubcategory, token: str = Depends(s.oauth2_scheme)):
    """
    Notes:
    - Label fields that should be set to `null` should be passed with the value `__null__`.
    - Omitted fields or fields with the value `None` will not be updated.
    """
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A']:
            raise HTTPException(status_code=401, detail="User does not have privileges")

        cursor.execute("SELECT subcategory_id FROM product_subcategories WHERE subcategory_id = %s", (subcategory_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail=f"Product subcategory {subcategory_id} not found.")

        update_fields = []
        update_values = []

        if subcategory_info.category_id is not None:
            cursor.execute("SELECT category_id FROM product_categories WHERE category_id = %s", (subcategory_info.category_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail=f"Product category {subcategory_info.category_id} not found.")
            update_fields.append("category_id = %s")
            update_values.append(subcategory_info.category_id)

        if subcategory_info.subcategory_name is not None:
            update_fields.append("subcategory_name = %s")
            update_values.append(subcategory_info.subcategory_name)

        if subcategory_info.subcategory_description is not None:
            update_fields.append("subcategory_description = %s")
            update_values.append(subcategory_info.subcategory_description)

        if subcategory_info.catalog_yn is not None:
            update_fields.append("catalog_yn = %s")
            update_values.append('Y' if subcategory_info.catalog_yn == 'Y' else 'N')

        # Handle new fields with null check
        if subcategory_info.term_label is not None:
            if subcategory_info.term_label == "__null__":
                update_fields.append("term_label = NULL")
            else:
                update_fields.append("term_label = %s")
                update_values.append(subcategory_info.term_label)

        if subcategory_info.percentage_label is not None:
            if subcategory_info.percentage_label == "__null__":
                update_fields.append("percentage_label = NULL")
            else:
                update_fields.append("percentage_label = %s")
                update_values.append(subcategory_info.percentage_label)

        if subcategory_info.mon_amt_label is not None:
            if subcategory_info.mon_amt_label == "__null__":
                update_fields.append("mon_amt_label = NULL")
            else:
                update_fields.append("mon_amt_label = %s")
                update_values.append(subcategory_info.mon_amt_label)

        if update_fields:
            update_values.append(subcategory_id)
            stmt = f"UPDATE product_subcategories SET {', '.join(update_fields)} WHERE subcategory_id = %s"
            cursor.execute(stmt, tuple(update_values))
            cnx.commit()

        cursor.execute("""
            SELECT subcategory_id, category_id, subcategory_name, subcategory_description, catalog_yn, 
                   term_label, percentage_label, mon_amt_label 
            FROM product_subcategories 
            WHERE subcategory_id = %s
        """, (subcategory_id,))
        row = cursor.fetchone()
        return s.ProductSubcategories(
            subcategory_id=row[0],
            category_id=row[1],
            subcategory_name=row[2],
            subcategory_description=row[3],
            catalog_yn=row[4],
            term_label=row[5],
            percentage_label=row[6],
            mon_amt_label=row[7]
        )
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        cnx.close()


@router.delete("/subcategory/{subcategory_id}")
async def delete_subcategory(subcategory_id: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A']:
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT subcategory_id FROM product_subcategories WHERE subcategory_id = %s", (subcategory_id,))
        if cursor.fetchone() is None:
            raise HTTPException(404, f"Product subcategory {subcategory_id} not found.")

        cursor.execute("SELECT count(*) FROM products WHERE subcategory_id = %s", (subcategory_id,))
        if cursor.fetchone()[0] != 0:
            raise HTTPException(400, "There are products in this subcategory; therefore, you cannot delete it.")

        cursor.execute("DELETE FROM product_subcategories WHERE subcategory_id = %s", (subcategory_id,))
        cnx.commit()
        return {"status": f"Successfully deleted {subcategory_id}"}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, str(err))
    finally:
        cursor.close()
        cnx.close()


@router.get("/products", response_model=List[s.Product])
async def list_products(
        category_id: Optional[str] = None,
        subcategory_id: Optional[str] = None,
        only_active_yn: str = 'Y',
        include_drafts_yn: str = 'N',
        token: str | None = Depends(s.optional_oauth2_scheme)
):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        sql = """
        SELECT p.product_id, p.category_id, pc.category_name, p.name, p.description, p.terms_and_conditions, 
               p.currency, p.term, p.percentage, p.monetary_amount, p.percentage_label, p.mon_amt_label, 
               p.available_from, p.available_till, COALESCE(p.picture_name, p.category_id), p.subcategory_id,
               p.draft_yn, p.draft_owner
        FROM products p
        JOIN product_categories pc ON pc.category_id = p.category_id
        WHERE 1=1
        """

        if only_active_yn == 'Y':
            sql += " AND p.available_from <= NOW() AND COALESCE(p.available_till, NOW()) >= NOW()"

        params = []
        if include_drafts_yn == 'Y':
            usr_account_id, usr_account_role = h.verify_token(token)
            if usr_account_role not in ['C', 'A']:
                raise HTTPException(401, "User does not have privileges")
        else:
            sql += " AND p.draft_yn = 'N'"

        if category_id is not None:
            sql += " AND p.category_id = %s"
            params.append(category_id)

        if subcategory_id is not None:
            sql += " AND p.subcategory_id = %s"
            params.append(subcategory_id)

        cursor.execute(sql, params)
        products = cursor.fetchall()

        if not products:
            return []

        product_list = [
            s.Product(
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
                available_from=str(prod[12].strftime('%Y-%m-%d')) if prod[12] is not None else None,
                available_till=str(prod[13].strftime('%Y-%m-%d')) if prod[13] is not None else None,
                picture_name=prod[14],
                subcategory_id=prod[15],
                draft_yn=prod[16],
                draft_owner=prod[17]
            ) for prod in products
        ]

        return product_list

    except mysql.connector.Error as err:
        raise HTTPException(500, str(err))
    finally:
        cursor.close()
        cnx.close()


@router.get("/{product_id}", response_model=s.Product)
async def info_about_product(product_id: int, token: str | None = Depends(s.optional_oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        sql = """
        SELECT p.product_id, p.category_id, pc.category_name, p.name, p.description, p.terms_and_conditions, 
               p.currency, p.term, p.percentage, p.monetary_amount, p.percentage_label, p.mon_amt_label, 
               p.available_from, p.available_till, COALESCE(p.picture_name, p.category_id), 
               p.draft_yn, p.draft_owner, p.term_label
        FROM products p
        LEFT JOIN product_categories pc ON pc.category_id = p.category_id
        WHERE p.product_id = %s
        """

        cursor.execute(sql, (product_id,))
        product = cursor.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            usr_account_id, usr_account_role = h.verify_token(token)
        except Exception:
            usr_account_id, usr_account_role = None, None

        # Determine which SQL query to use based on whether the product is a draft and user privileges
        if product[15] == 'Y':  # if a draft
            if product[16] != usr_account_id and usr_account_role not in ['C', 'A']:
                raise HTTPException(401, "User does not have privileges")
            stmt = """
                SELECT order_no, column_name, customer_visible_yn, customer_populatable_yn, column_type, 
                       default_value, exercise_date_yn, available_before 
                FROM draft_product_custom_column_def 
                WHERE product_id = %s
            """
        else:
            if usr_account_role in ['A', 'C', 'E']:
                stmt = """
                    SELECT pcc_id, column_name, customer_visible_yn, customer_populatable_yn, column_type, 
                           default_value, exercise_date_yn, available_before 
                    FROM product_custom_column_def 
                    WHERE product_id = %s
                """
            else:
                stmt = """
                    SELECT pcc_id, column_name, customer_visible_yn, customer_populatable_yn, column_type, 
                           default_value, exercise_date_yn, available_before 
                    FROM product_custom_column_def 
                    WHERE product_id = %s AND customer_visible_yn = 'Y'
                """

        cursor.execute(stmt, (product_id,))
        rows = cursor.fetchall()
        custom_columns = [
            s.ProductCustomColumnDefinition(
                pcc_id=row[0] if product[15] == 'N' else None,
                order_no=row[0] if product[15] == 'Y' else None,
                column_name=row[1],
                customer_visible_yn=row[2],
                customer_populatable_yn=row[3],
                column_type=row[4],
                default_value=row[5],
                exercise_date_yn=str(row[6]) if row[6] is not None else None,
                available_before=row[7]
            ) for row in rows
        ]

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
            term_label=product[17],
            percentage_label=product[10],
            mon_amt_label=product[11],
            available_from=str(product[12].strftime('%Y-%m-%d')) if product[12] is not None else None,
            available_till=str(product[13].strftime('%Y-%m-%d')) if product[13] is not None else None,
            picture_name=product[14],
            draft_yn=product[15],
            draft_owner=product[16],
            custom_columns=custom_columns
        )

        return product_data

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        cnx.close()


@router.get("/drafts/", response_model=List[s.Product])
async def list_products(view_all_yn: Optional[str] = 'N', token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:  # Only certain roles can see drafts
            raise HTTPException(401, "User does not have privileges")

        sql = """
        SELECT p.product_id, p.category_id, pc.category_name, p.name, p.description, p.terms_and_conditions, 
               p.currency, p.term, p.percentage, p.monetary_amount, p.percentage_label, p.mon_amt_label, 
               p.available_from, p.available_till, COALESCE(p.picture_name, p.category_id), p.subcategory_id,
               p.draft_yn, p.draft_owner
        FROM products p
        JOIN product_categories pc ON pc.category_id = p.category_id
        WHERE p.draft_yn = 'Y'
        """

        params = []
        if view_all_yn == 'Y':
            if usr_account_role not in ['C', 'A']:  # only Admins / C-Suite people can see all drafts
                raise HTTPException(401, "User does not have privileges")
        else:
            sql += " AND p.draft_owner = %s"
            params.append(usr_account_id)

        cursor.execute(sql, params)
        products = cursor.fetchall()

        if not products:
            return []

        product_list = [
            s.Product(
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
                available_from=str(prod[12].strftime('%Y-%m-%d')) if prod[12] is not None else None,
                available_till=str(prod[13].strftime('%Y-%m-%d')) if prod[13] is not None else None,
                picture_name=prod[14],
                subcategory_id=prod[15],
                draft_yn=prod[16],
                draft_owner=prod[17]
            ) for prod in products
        ]

        return product_list

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        cnx.close()


@router.post("/draft")
async def create_new_product_draft(product: s.NewProduct, token: str = Depends(s.oauth2_scheme)):
    """
    Notes:
    - The API allows regular employees to create product drafts, but the product's `available_from` and `available_till`
      will be null, so that they cannot be shown in the product catalog. This is done so that regular employees can
      create custom products, but not actual products.
    - Regardless of the `draft_yn` provided, it will always be set to 'Y'. The API does not allow creating a product
      directly without reviewing the draft at least once.
    """
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:  # Only certain roles can create products
            raise HTTPException(401, "User does not have privileges")

        stmt = """
        INSERT INTO products (category_id, subcategory_id, name, description, currency, term, percentage, 
                              monetary_amount, percentage_label, mon_amt_label, available_from, available_till, 
                              draft_yn, draft_owner, terms_and_conditions, picture_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(stmt, (
            product.category_id, product.subcategory_id, product.name, product.description,
            product.currency, product.term, product.percentage, product.monetary_amount,
            product.percentage_label, product.mon_amt_label,
            product.available_from if usr_account_role in ['C', 'A'] else None,
            product.available_till if usr_account_role in ['C', 'A'] else None,
            'Y', usr_account_id, product.terms_and_conditions, product.picture_name
        ))

        cursor.execute("SELECT LAST_INSERT_ID()")
        product_id = cursor.fetchone()[0]

        custom_column_count = 0
        if product.custom_columns:
            ordered_columns = sorted(product.custom_columns, key=lambda column: column.order_no or 100)
            for index, column in enumerate(ordered_columns):
                column.order_no = index

            sql_insert = """
            INSERT INTO draft_product_custom_column_def 
            (product_id, order_no, column_name, customer_visible_yn, customer_populatable_yn, column_type, 
             default_value, exercise_date_yn, available_before)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = [
                (
                    product_id,
                    column.order_no,
                    column.column_name,
                    'Y' if column.customer_visible_yn == 'Y' else 'N',
                    'Y' if column.customer_populatable_yn == 'Y' else 'N',
                    column.column_type,
                    column.default_value if column.default_value else None,
                    column.exercise_date_yn,
                    column.available_before
                ) for column in ordered_columns
            ]

            # Use executemany to insert multiple rows
            cursor.executemany(sql_insert, values)
            custom_column_count = cursor.rowcount

        cnx.commit()
        return {"status": f"Success! Draft product created with ID: {product_id}, and {custom_column_count} custom columns",
                "product_id": product_id}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.patch("/{product_id}")
async def modify_product(product_id: int, product: s.AmendProduct, token: str = Depends(s.oauth2_scheme)):
    """
    Notes:
    - Fields that should be set to `null` should be passed with the value `__null__`.
    - Omitted fields or fields with the value `None` will not be updated.
    """
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['A']:  # Only admins can change non-draft products
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT draft_yn FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_id} not found.")

        update_fields = {}

        def check_field(field_name, value):
            if value == "__null__":
                update_fields[field_name] = None
            elif value is not None:
                update_fields[field_name] = value

        check_field("category_id", product.category_id)
        check_field("subcategory_id", product.subcategory_id)
        check_field("name", product.name)
        check_field("description", product.description)
        check_field("currency", product.currency)
        check_field("term", product.term)
        check_field("percentage", product.percentage)
        check_field("monetary_amount", product.monetary_amount)
        check_field("term_label", product.term_label)
        check_field("percentage_label", product.percentage_label)
        check_field("mon_amt_label", product.mon_amt_label)
        check_field("available_from", product.available_from)
        check_field("available_till", product.available_till)
        check_field("picture_name", product.picture_name)
        check_field("draft_owner", product.draft_owner)
        check_field("terms_and_conditions", product.terms_and_conditions)

        if not update_fields:
            raise HTTPException(400, "No fields to update")

        set_clause = ", ".join([f"{key} = %s" for key in update_fields.keys()])
        values = list(update_fields.values())
        values.append(product_id)

        stmt = f"UPDATE products SET {set_clause} WHERE product_id = %s"
        cursor.execute(stmt, values)

        cnx.commit()
        return {"status": f"Success! Product {product_id} has been updated"}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.put("/{product_id}/availability")
async def modify_product_availability(product_id: int, product: s.ProductAvailability, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['A', 'C']:  # Only admins or C-Suite can change availability of non-draft products
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT draft_yn FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_id} not found.")

        stmt = "UPDATE products SET available_from = %s, available_till = %s WHERE product_id = %s"
        cursor.execute(stmt, (product.available_from, product.available_till, product_id))
        cnx.commit()
        return {"status": "Success!"}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.post("/{product_id}/duplicate")
async def duplicate_product(product_id: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['A', 'C', 'E']:  # Only authorized roles can duplicate products
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT draft_yn FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_id} not found.")

        cursor.execute("SELECT clone_product_and_custom_columns(%s, %s)", (product_id, usr_account_id))
        new_product_id = cursor.fetchone()[0]
        cnx.commit()
        return {"status": f"Success! Product {new_product_id} created.", "product_id": new_product_id}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.patch("/draft/{product_id}")
async def modify_product_draft(product_id: int, product: s.AmendProduct, token: str = Depends(s.oauth2_scheme)):
    """
    Notes:
    - Fields that should be set to `null` should be passed with the value `__null__`.
    - Omitted fields or fields with the value `None` will not be updated.
    """
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:  # Only specific roles can modify drafts
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT draft_yn FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_id} not found.")
        if result[0] != 'Y':
            raise HTTPException(403, f"Product {product_id} is not a draft.")

        update_fields = {}

        def check_field(field_name, value):
            if value == "__null__":
                update_fields[field_name] = None
            elif value is not None:
                update_fields[field_name] = value

        check_field("category_id", product.category_id)
        check_field("subcategory_id", product.subcategory_id)
        check_field("name", product.name)
        check_field("description", product.description)
        check_field("currency", product.currency)
        check_field("term", product.term)
        check_field("percentage", product.percentage)
        check_field("monetary_amount", product.monetary_amount)
        check_field("term_label", product.term_label)
        check_field("percentage_label", product.percentage_label)
        check_field("mon_amt_label", product.mon_amt_label)
        check_field("available_from", product.available_from)
        check_field("available_till", product.available_till)
        check_field("picture_name", product.picture_name)
        check_field("draft_owner", product.draft_owner)
        check_field("terms_and_conditions", product.terms_and_conditions)

        if product.draft_yn is not None:
            if usr_account_role in ['C', 'A']:
                if product.draft_yn == 'N':
                    update_fields["draft_yn"] = 'N'
                    update_fields["draft_owner"] = None
                else:
                    update_fields["draft_yn"] = 'Y'

        if not update_fields:
            raise HTTPException(400, "No fields to update")

        set_clause = ", ".join([f"{key} = %s" for key in update_fields.keys()])
        values = list(update_fields.values())
        values.append(product_id)

        stmt = f"UPDATE products SET {set_clause} WHERE product_id = %s"
        cursor.execute(stmt, values)

        if update_fields.get("draft_yn") == 'N':
            cursor.execute("SELECT copy_product_custom_column_def(%s)", (product_id,))

        cnx.commit()
        return {"status": f"Success! Draft product with ID {product_id} has been updated"}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.delete("/draft/{product_id}")
async def delete_product_draft(product_id: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:  # Only specific roles can delete drafts
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT draft_yn FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        if result is None or result[0] == 'N':
            raise HTTPException(404, f"Product {product_id} either does not exist or is not a draft.")

        cursor.execute("DELETE FROM draft_product_custom_column_def WHERE product_id = %s", (product_id,))
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        cnx.commit()
        return {"status": f"Success! Product {product_id} has successfully been deleted."}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.put("/draft/{product_id}/custom-columns")
async def modify_a_draft_products_custom_columns(
    product_id: int,
    columns: List[s.NewProductCustomColumnDefinition],
    token: str = Depends(s.oauth2_scheme)
):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:  # Only specific roles can modify custom columns
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT draft_owner FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_id} does not exist.")
        draft_owner = result[0]

        # Ensure it's the user's draft or the user is a C-Suit/Admin
        if draft_owner != usr_account_id and usr_account_role not in ['C', 'A']:
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("DELETE FROM draft_product_custom_column_def WHERE product_id = %s", (product_id,))

        if not columns:
            cnx.commit()
            return {"status": "Success!"}

        ordered_columns = sorted(columns, key=lambda column: column.order_no or 100)
        for index, column in enumerate(ordered_columns):
            column.order_no = index

        sql_insert = """
        INSERT INTO draft_product_custom_column_def 
        (product_id, order_no, column_name, customer_visible_yn, customer_populatable_yn, column_type, 
         default_value, exercise_date_yn, available_before)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = [
            (
                product_id,
                column.order_no,
                column.column_name,
                'Y' if column.customer_visible_yn == 'Y' else 'N',
                'Y' if column.customer_populatable_yn == 'Y' else 'N',
                column.column_type,
                column.default_value if column.default_value else None,
                column.exercise_date_yn,
                column.available_before
            ) for column in ordered_columns
        ]

        cursor.executemany(sql_insert, values)
        custom_column_count = cursor.rowcount
        cnx.commit()
        return {"status": f"Success! {custom_column_count} custom columns have been added for {product_id}."}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.get("/instances/", response_model=List[s.ProductCard])
async def get_product_instancess(
    status_code: Optional[List[str]] = Query(None),
    product_id: Optional[int] = None,
    product_uid: Optional[int] = None,
    contract_id: Optional[int] = None,
    token: str = Depends(s.oauth2_scheme)
):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:  # Only specific roles can view product instances
            raise HTTPException(401, "User does not have privileges")

        query = """
            SELECT 
                pi.product_uid, pi.application_id, pi.contract_id, appl.approved_by,
                p.name, p.description, COALESCE(pi.amount, appl.amount_requested) AS amount, 
                pi.status_code, ps.status_name, p.category_id, p.currency, 
                ac.first_name, ac.last_name, ac.account_id, COALESCE(p.picture_name, p.category_id)
            FROM product_instances pi
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

        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            return []

        result = [
            s.ProductCard(
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
            ) for row in rows
        ]

        return result
    except mysql.connector.Error as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.get("/instance/{product_uid}", response_model=Union[s.ProductInstancePrivate, s.ProductInstancePublic])
async def get_product_instances(product_uid: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        cursor.execute("SELECT account_id FROM product_instances WHERE product_uid = %s", (product_uid,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_uid} does not exist")
        account_id = result[0]

        # Ensure user has privileges or is the owner of the product instance
        if usr_account_role not in ['C', 'A', 'E'] and account_id != usr_account_id:
            raise HTTPException(401, "User does not have privileges")

        # Fetch status updates
        stmt = """
        SELECT product_uid, is_code, status_name, status_description, update_dt, update_user, ac.first_name, ac.last_name, 
               update_note, update_note_public_yn
        FROM (
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
            JOIN product_instances pi ON pi.application_id = appl.application_id
            JOIN product_statuses ps ON ps.code = 'APL' 
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
        cursor.execute(stmt, (product_uid,))
        res = cursor.fetchall()

        statuses = [
            s.StatusUpdates(
                status_code=status[1],
                status_name=status[2],
                status_description=status[3],
                status_update_dt=str(status[4]),
                update_user=status[5],
                first_name=status[6],
                last_name=status[7],
                update_note=status[8] if status[8] and (
                            status[9] == 'Y' or usr_account_role in ['C', 'A', 'E']) else None,
                public_yn=status[9] if status[9] and (status[9] == 'Y' or usr_account_role in ['C', 'A', 'E']) else None
            )
            for status in res
        ]

        # Fetch custom columns
        stmt = """
        SELECT pccv.pcc_uid, pccv.pcc_id, pccv.product_uid, pccd.column_name, 
               pccd.customer_populatable_yn, pccd.customer_visible_yn, pccd.column_type,
               pccv.int_value, pccv.float_value, pccv.varchar_value, pccv.text_value, pccv.date_value, pccv.datetime_value
        FROM product_custom_column_values pccv 
        JOIN product_custom_column_def pccd ON pccd.pcc_id = pccv.pcc_id
        WHERE product_uid = %s
        """
        cursor.execute(stmt, (product_uid,))
        product_custom_columns = []
        rows = cursor.fetchall()
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
                    date_value=str(row[11]),
                    datetime_value=str(row[12])
                ))

        # Fetch product instance details
        stmt = """
        SELECT pi.product_uid, pi.account_id, pi.status_code, ps.status_name, ps.status_description, pi.amount, 
               pi.contract_id, pi.product_start_date, pi.product_end_date, pi.actual_end_date, pi.special_notes, pi.application_id, 
               appl.approved_by, appl.amount_requested, appl.special_notes, appl.collateral, appl.approved_yn, appl.approval_dt, 
               pi.yield, pi.actual_revenue, appl.product_id, pi.expected_revenue, 
               CASE WHEN appl.standard_yn = 'Y' THEN 'Standard' ELSE 'Custom' END AS standard, 
               notifications_yn
        FROM product_instances pi 
        LEFT JOIN applications appl ON appl.application_id = pi.application_id
        JOIN product_statuses ps ON ps.code = pi.status_code 
        WHERE pi.product_uid = %s
        """
        cursor.execute(stmt, (product_uid,))
        res = cursor.fetchone()

        # Determine the response model based on user role
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
                product_id=res[20],
                standard=res[22],
                notifications=res[23]
            )

        return prod
    except mysql.connector.Error as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.patch("/instance/{product_uid}/status/{new_status}")
async def update_product_status(
    product_uid: int,
    new_status: str,
    update_note: s.UpdateNoteModel = Body(),
    token: str = Depends(s.oauth2_scheme)
):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:  # Only specific roles can update statuses
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT status_code, notifications_yn FROM product_instances WHERE product_uid = %s", (product_uid,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_uid} does not exist")
        current_status, notifications_yn = result

        possible_future_statuses = h.available_next_status(current_status)
        if not any(d["status_code"] == new_status for d in possible_future_statuses):
            raise HTTPException(403, f"Status {new_status} not allowed after {current_status} or does not exist")

        if update_note.content is not None:
            stmt = """
            UPDATE product_instances SET 
                status_code = %s, 
                latest_update_user_id = %s, 
                latest_note = %s, 
                latest_note_public_yn = %s 
            WHERE product_uid = %s
            """
            cursor.execute(stmt, (new_status, usr_account_id, update_note.content,
                                  'Y' if update_note.public_yn == 'Y' else 'N', product_uid))
        else:
            stmt = "UPDATE product_instances SET status_code = %s, latest_update_user_id = %s WHERE product_uid = %s"
            cursor.execute(stmt, (new_status, usr_account_id, product_uid))

        cnx.commit()

        if new_status in ['APR', 'DEN']:
            stmt = """
            UPDATE applications 
            SET approved_yn = %s, approved_by = %s, approval_dt = now()
            WHERE application_id = (SELECT application_id FROM product_instances WHERE product_uid = %s)
            """
            cursor.execute(stmt, ('Y' if new_status == 'APR' else 'N', usr_account_id, product_uid))
            cnx.commit()

            if new_status == 'APR':
                c.generate_contract_string(product_uid)

        if notifications_yn == 'Y':
            m.send_product_status_update_email(product_uid, new_status)
        elif notifications_yn == 'P' and new_status in ["AMD", "APR", "DEN", "CNL", "SGN", "NOR", "TRG", "DUE", "ORD", "CMP"]:
            m.send_product_status_update_email(product_uid, new_status)

        return {"status": "Success!"}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.patch("/instance/{product_uid}/status/{new_status}/client/")
async def client_update_product_status(
    product_uid: int,
    new_status: str,
    update_note: s.UpdateNoteModel = Body(),
    token: str = Depends(s.oauth2_scheme)
):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        cursor.execute(
            "SELECT status_code, account_id, notifications_yn FROM product_instances WHERE product_uid = %s",
            (product_uid,)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_uid} does not exist")
        current_status, account_id, notifications_yn = result

        # Ensure the user is the owner of the product instance
        if account_id != usr_account_id:
            raise HTTPException(401, "User does not have privileges")

        possible_future_statuses = h.available_next_status(current_status)
        if not any(d["status_code"] == new_status for d in possible_future_statuses):
            raise HTTPException(403, f"Status {new_status} not allowed after {current_status} or does not exist")
        if new_status not in ["CNL", "AGR", "DIS"]:
            raise HTTPException(403, "This action cannot be performed by the client")

        if update_note.content is not None:
            stmt = """
            UPDATE product_instances SET 
                status_code = %s, 
                latest_update_user_id = %s, 
                latest_note = %s, 
                latest_note_public_yn = %s 
            WHERE product_uid = %s
            """
            cursor.execute(stmt, (new_status, usr_account_id, update_note.content,
                                  'Y' if update_note.public_yn == 'Y' else 'N', product_uid))
        else:
            stmt = "UPDATE product_instances SET status_code = %s, latest_update_user_id = %s WHERE product_uid = %s"
            cursor.execute(stmt, (new_status, usr_account_id, product_uid))

        cnx.commit()

        if notifications_yn == 'Y':
            m.send_product_status_update_email(product_uid, new_status)
        elif notifications_yn == "P" and new_status == "CNL":
            m.send_product_status_update_email(product_uid, new_status)

        return {"status": "Success!"}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.patch("/instance/{product_uid}")
async def update_product_instances(
    product_uid: int,
    amendments: s.AmendProductInstance,
    token: str = Depends(s.oauth2_scheme)
):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT status_code FROM product_instances WHERE product_uid = %s", (product_uid,))
        cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(404, f"Product {product_uid} does not exist")

        update_fields = []
        params = []

        # Collect fields to update based on provided amendments
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

        if not update_fields and not amendments.product_custom_columns:
            raise HTTPException(400, "No fields to update")

        # Execute update for product instance fields
        if update_fields:
            params.append(product_uid)
            stmt = f"""
            UPDATE product_instances
            SET {', '.join(update_fields)}
            WHERE product_uid = %s
            """
            cursor.execute(stmt, tuple(params))
            cnx.commit()

        # Handle custom columns updates if provided
        if amendments.product_custom_columns:
            for pcc in amendments.product_custom_columns:
                h.update_product_custom_fields(pcc, False)

        return {"message": "Product updated successfully"}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.post("/instance/{product_uid}/sign-contract")
async def digitally_sign_contract(product_uid: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        cursor.execute(
            "SELECT account_id, status_code, contract_id FROM product_instances WHERE product_uid = %s",
            (product_uid,)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"No product with Product UID {product_uid} found.")
        account_id, status_code, contract_id = result

        if account_id != usr_account_id:
            raise HTTPException(401, "User is not authorized")
        if status_code != "SGN":
            raise HTTPException(403, "Signing not allowed for this product status.")

        cursor.execute("SELECT verification FROM accounts WHERE account_id = %s", (usr_account_id,))
        verification = cursor.fetchone()
        if verification is None or verification[0] != 'Y':
            raise HTTPException(401, "Unverified accounts cannot sign a contract.")

        # Sign the contract
        c.sign_contract(contract_id, usr_account_id)

        # Update the product instance status to 'AWT' (Awaiting)
        stmt = "UPDATE product_instances SET status_code = 'AWT', latest_update_user_id = %s WHERE product_uid = %s"
        cursor.execute(stmt, (usr_account_id, product_uid))
        cnx.commit()

        # Send the contract email
        m.send_contract_email(product_uid)

        return {"status": "Success!"}
    except mysql.connector.Error as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.get("/instance/{product_uid}/contract/")
async def get_pdf_contract(product_uid: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        cursor.execute("SELECT account_id, contract_id FROM product_instances WHERE product_uid = %s", (product_uid,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_uid} not found")

        account_id, contract_id = result

        # Check if the user has the necessary privileges to access the contract
        if usr_account_role not in ['C', 'A', 'E'] and account_id != usr_account_id:
            raise HTTPException(401, "User does not have privileges.")

        # Generate the contract PDF buffer
        buffer = c.contract_buffer(contract_id)

        # Create and return a StreamingResponse from the buffer
        return StreamingResponse(
            buffer,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment;filename=contract_{contract_id}.pdf"}
        )
    except Exception as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.put("/instance/{product_uid}/notifications/{new_preference}")
async def update_product_notifications_status(
        product_uid: int,
        new_preference: str,
        token: str = Depends(s.oauth2_scheme)
):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        cursor.execute("SELECT account_id FROM product_instances WHERE product_uid = %s", (product_uid,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(404, f"Product {product_uid} not found")

        account_id = result[0]

        # Check if the user has the necessary privileges to update the notification preference
        if usr_account_role not in ['C', 'A', 'E'] and account_id != usr_account_id:
            raise HTTPException(401, "User does not have privileges.")

        # Validate the new preference
        if new_preference not in ['Y', 'N', 'P']:
            raise HTTPException(403, f"{new_preference} is not a valid notification preference status")

        # Update the notification preference
        cursor.execute(
            "UPDATE product_instances SET notifications_yn = %s WHERE product_uid = %s",
            (new_preference, product_uid)
        )
        cnx.commit()

        return {"status": "Success!"}
    except mysql.connector.Error as e:
        cnx.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        cursor.close()
        cnx.close()

