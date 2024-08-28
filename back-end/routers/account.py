from fastapi import APIRouter, HTTPException, Header, Query, Depends, Response
from typing import Annotated, Optional, List
import re
import mysql.connector
from dependencies.database import get_db_connection
from dependencies import database as db, helpers as h, schemas as s, mail as m

router = APIRouter(
    prefix="/account",
    tags=["Account"]
)


@router.get("")
async def get_accounts(
        country_code: Optional[List[str]] = Query(None),
        user_role: Optional[List[str]] = Query(None),
        verification: Optional[List[str]] = Query(None),
        account_group: Optional[List[str]] = Query(None),
        token: str = Depends(s.oauth2_scheme)
):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)
        if usr_account_role not in ['C', 'A', 'E']:
            raise HTTPException(401, "User does not have privileges")

        # Prepare SQL query with dynamic filters
        filters = []
        params = []

        if country_code:
            filters.append("a.country_code IN (%s)" % ','.join(['%s'] * len(country_code)))
            params.extend(country_code)
        if user_role:
            filters.append("a.user_role IN (%s)" % ','.join(['%s'] * len(user_role)))
            params.extend(user_role)
        if verification:
            filters.append("a.verification IN (%s)" % ','.join(['%s'] * len(verification)))
            params.extend(verification)
        if account_group:
            filters.append("a.account_group IN (%s)" % ','.join(['%s'] * len(account_group)))
            params.extend(account_group)

        # Base SQL query
        stmt = """
        SELECT a.account_id, a.first_name, a.last_name, a.email, a.phone, a.country_code, 
               a.address, a.user_role, ur.description, a.verification, v.description, 
               a.account_group, ag.group_name, ag.group_description, a.created_dt
        FROM accounts a
        JOIN user_roles ur ON ur.role = a.user_role
        JOIN verifications v ON v.verification_status = a.verification
        JOIN account_groups ag ON ag.group_code = a.account_group
        """

        # Append filters if there are any
        if filters:
            stmt += " WHERE " + " AND ".join(filters)

        cursor.execute(stmt, tuple(params))

        # Fetch and format results
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
        } for row in cursor.fetchall()]

        return result
    except mysql.connector.Error as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.get("/search", response_model=List[s.AccountCard])
async def search_for_account(search_str: str, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        if usr_account_role not in ['C', 'A', 'E']:
            raise HTTPException(401, "User does not have privileges")

        # Define regular expressions
        patterns = {
            "name": r"^[a-zA-Z0-9]+$",
            "email": r"^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$",
            "group": r"^group:[A-Z]{1,3}$",
            "country_code": r"^country_code:[A-Z]{1,3}$",
            "phone": r"^phone:[+0-9]{4,15}$"
        }

        # Split the input string by whitespace
        words = search_str.split()

        # Initialize lists to hold matched words
        names = []
        email = None
        group = None
        phone = None
        country_code = None

        # Check each word against the regular expressions
        for word in words:
            if re.match(patterns["name"], word):
                names.append(word)
            elif re.match(patterns["email"], word):
                email = word
            elif re.match(patterns["group"], word):
                group = word.split(":")[1]
            elif re.match(patterns["country_code"], word):
                country_code = word.split(":")[1]
            elif re.match(patterns["phone"], word):
                phone = word.split(":")[1]

        # Construct the SQL query
        query = """
        SELECT account_id, first_name, last_name, email, phone, verification, account_group, ag.group_name
        FROM accounts ac 
        JOIN account_groups ag ON ag.group_code = ac.account_group
        WHERE """
        conditions = []
        bindings = []

        if names:
            name_conditions = " OR ".join(["LOWER(first_name) = %s", "LOWER(last_name) = %s"] * len(names))
            conditions.append(f"({name_conditions})")
            for name in names:
                bindings.extend([name.lower(), name.lower()])
        if email:
            conditions.append("LOWER(email) = %s")
            bindings.append(email.lower())
        if group:
            conditions.append("UPPER(account_group) = %s")
            bindings.append(group.upper())
        if country_code:
            conditions.append("UPPER(country_code) = %s")
            bindings.append(country_code.upper())
        if phone:
            conditions.append("phone LIKE %s")
            bindings.append('%' + phone + '%')

        if conditions:
            query += " AND ".join(conditions)
        else:
            query += " 1 = 1"  # No specific conditions; avoid selecting all

        cursor.execute(query, tuple(bindings))

        rows = cursor.fetchall()
        if cursor.rowcount == 0:
            return []

        return [s.AccountCard(
            account_id=row[0],
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            phone=row[4],
            verification_code=row[5],
            verification_emoji=h.verification_emoji(row[5]),
            account_group_code=row[6],
            account_group_name=row[7]
        ) for row in rows]

    except Exception as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.get("/{account_id}")
async def get_account_info(account_id: int, response: Response, token: str = Depends(s.oauth2_scheme)):
    # Set Cache-Control header to prevent caching
    response.headers["Cache-Control"] = "no-store"

    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        if usr_account_role not in ['C', 'A', 'E'] and account_id != usr_account_id:
            raise HTTPException(401, "User does not have privileges")

        stmt = """
        SELECT SQL_NO_CACHE a.account_id, a.first_name, a.last_name, a.email, a.phone, a.country_code, 
        CASE 
            WHEN country_code = 'BGR' THEN 'Bulgaria' 
            WHEN country_code = 'USA' THEN 'United States' 
            WHEN country_code = 'OTH' THEN 'Other' 
            ELSE country_code 
        END AS country,
        a.address, a.user_role, ur.description, a.verification, v.description, a.account_group, 
        ag.group_name, ag.group_description, created_dt 
        FROM accounts a 
        JOIN user_roles ur ON ur.role = a.user_role 
        JOIN verifications v ON v.verification_status = a.verification 
        JOIN account_groups ag ON ag.group_code = a.account_group
        WHERE a.account_id = %s
        """

        cursor.execute(stmt, (account_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(404, f"Account {account_id} does not exist")

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

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.post("/")
async def create_account():
    raise HTTPException(501)


@router.post("/{account_id}/send-verification-email")
async def send_verification_email(account_id: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        if usr_account_role not in ['C', 'A', 'E'] and usr_account_id != account_id:
            raise HTTPException(401, "User does not have privileges")

        cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
        _ = cursor.fetchall()
        if cursor.rowcount != 1:
            raise HTTPException(404, "Account not found")

        m.send_verification_email(account_id)
        return {"message": "Success!"}

    except Exception as err:
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.post("/verify")
async def verify_account(token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        stmt = "UPDATE accounts SET verification = 'Y' WHERE account_id = %s"
        cursor.execute(stmt, (usr_account_id,))
        cnx.commit()

        return {"status": "Success"}

    except Exception as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.patch("/{account_id}/verification")
async def change_account_verification_status(account_id: int, new_verification_code: str,
                                             token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        # Authorization check
        if usr_account_role not in ['C', 'A', 'E'] and (new_verification_code != 'C' or account_id != usr_account_id):
            raise HTTPException(401, "User does not have privileges")

        # Check if the account exists
        cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
        _ = cursor.fetchall()
        if cursor.rowcount != 1:
            raise HTTPException(404, "Account not found")

        # Check if the verification code is valid
        cursor.execute("SELECT verification_status FROM verifications WHERE verification_status = %s",
                       (new_verification_code,))
        _ = cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(409, "Not a valid verification_code")

        # If verification code is 'C', send a verification email
        if new_verification_code == 'C':
            m.send_verification_email(account_id)

        # Update the verification status
        stmt = "UPDATE accounts SET verification = %s WHERE account_id = %s"
        cursor.execute(stmt, (new_verification_code, account_id))
        cnx.commit()

        return {"status": "Success!"}

    except Exception as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")
    finally:
        cursor.close()
        cnx.close()


@router.patch("/{account_id}/information")
async def update_account_information(account_id: int, data: s.AmendAccount, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        # Check if the user has the right privileges
        if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
            raise HTTPException(401, "User does not have privileges")

        # Check if the account exists
        cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
        _ = cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(404, f"Account {account_id} does not exist")

        # Update phone if provided and valid
        if data.phone is not None:
            if len(data.phone) > 15:
                raise HTTPException(422, "Phone is too long")
            cursor.execute("UPDATE accounts SET phone = %s WHERE account_id = %s", (data.phone, account_id))
            cnx.commit()

        # Update email if provided and valid, and reset verification status
        if data.email is not None:
            if len(data.email) > 255:
                raise HTTPException(422, "Email is too long")
            cursor.execute("UPDATE accounts SET email = %s WHERE account_id = %s", (data.email, account_id))
            cursor.execute("UPDATE accounts SET verification = 'R' WHERE account_id = %s", (account_id,))
            cnx.commit()

        # Update country_code if provided and valid
        if data.country_code is not None:
            if data.country_code not in ['BGR', 'USA', 'OTH']:
                raise HTTPException(422, "Invalid country code")
            cursor.execute("UPDATE accounts SET country_code = %s WHERE account_id = %s", (data.country_code, account_id))
            cnx.commit()

        # Update address if provided
        if data.address is not None:
            cursor.execute("UPDATE accounts SET address = %s WHERE account_id = %s", (data.address, account_id))
            cnx.commit()

        return {"status": "Success!"}

    except Exception as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")

    finally:
        cursor.close()
        cnx.close()


@router.patch("/{account_id}/group")
async def update_account_group(account_id: int, data: s.AmendAccountGroup, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        # Check if the user has the right privileges
        if usr_account_role not in ['C', 'A', 'E'] and not account_id == usr_account_id:
            raise HTTPException(401, "User does not have privileges")

        # Check if the account exists
        cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
        _ = cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(404, f"Account {account_id} does not exist")

        # Check if the provided group code is valid
        cursor.execute("SELECT group_code FROM account_groups WHERE group_code = %s", (data.account_group_code,))
        _ = cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(409, "Not a valid group_code")

        # Update the account group
        stmt = "UPDATE accounts SET account_group = %s WHERE account_id = %s"
        cursor.execute(stmt, (data.account_group_code, account_id))
        cnx.commit()

        return {"status": "Success!"}

    except Exception as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")

    finally:
        cursor.close()
        cnx.close()


@router.put("/{account_id}/role/{new_user_role}")
async def update_account_role(account_id: int, new_user_role: str, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        # Check if the user has the right privileges
        if usr_account_role not in ['A', 'C']:
            raise HTTPException(401, "User does not have privileges")

        # Check if the account exists
        cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
        _ = cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(404, f"Account {account_id} does not exist")

        # Check if the provided user role is valid
        cursor.execute("SELECT role FROM user_roles WHERE role = %s", (new_user_role,))
        _ = cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(409, "Not a valid user role")

        # Update the user role
        update_role_stmt = "UPDATE accounts SET user_role = %s WHERE account_id = %s"
        cursor.execute(update_role_stmt, (new_user_role, account_id))

        # Determine the new account group based on the user role
        new_group = "EMP" if new_user_role in ["A", "C", "E"] else "FTC"
        update_group_stmt = "UPDATE accounts SET account_group = %s WHERE account_id = %s"
        cursor.execute(update_group_stmt, (new_group, account_id))

        cnx.commit()

        return {"status": "Success!"}

    except Exception as err:
        cnx.rollback()
        raise HTTPException(500, f"An error occurred: {err}")

    finally:
        cursor.close()
        cnx.close()


@router.post("/{account_id}/credentials")
async def update_account_credentials(account_id: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        # Check if the user has the appropriate privileges
        if usr_account_role not in ['C', 'A', 'E']:
            raise HTTPException(401, "User does not have privileges")

        # Verify if the account exists
        cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
        _ = cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(404, "Account not found")

        # Send password reset email
        m.send_password_reset_email(account_id)

        return {"status": "Success"}

    except Exception as err:
        raise HTTPException(500, f"An error occurred: {err}")

    finally:
        cursor.close()
        cnx.close()


@router.get("/{account_id}/products")
async def get_account_products(account_id: int, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        # Check user privileges
        if usr_account_role not in ['C', 'A', 'E'] and account_id != usr_account_id:
            raise HTTPException(401, "User does not have privileges")

        # SQL query to fetch product information related to the account
        stmt = """
            SELECT 
                pi.product_uid, pi.application_id, pi.contract_id, appl.approved_by,
                p.name, p.description, NVL(pi.amount, appl.amount_requested) AS amount, 
                pi.status_code, ps.status_name, p.category_id, p.currency, 
                nvl(p.picture_name, p.category_id)
            FROM product_instances pi
            JOIN applications appl ON appl.application_id = pi.application_id
            JOIN products p ON p.product_id = appl.product_id
            JOIN product_statuses ps ON ps.code = pi.status_code
            WHERE pi.account_id = %s
        """

        cursor.execute(stmt, (account_id,))
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(404, f"No product found for account {account_id}.")

        # Transforming fetched data into a list of ProductCard objects
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
            picture_name=row[11]
        ) for row in rows]

        return result

    except Exception as err:
        raise HTTPException(500, f"An error occurred: {err}")

    finally:
        cursor.close()
        cnx.close()


@router.post("/{account_id}/product/{product_id}")
async def product_sale(account_id: int, product_id: int, data: s.NewProductInstance, token: str = Depends(s.oauth2_scheme)):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        usr_account_id, usr_account_role = h.verify_token(token)

        # Check user privileges
        if usr_account_role not in ['C', 'A', 'E'] and account_id != usr_account_id:
            raise HTTPException(401, "User does not have privileges")

        # Validate that the account exists
        cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (account_id,))
        _ = cursor.fetchall()
        if cursor.rowcount == 0:
            raise HTTPException(404, f"Account {account_id} does not exist")

        # Validate `standard_yn` field
        standard_yn = 'N' if data.standard_yn not in ['Y', 'N'] else data.standard_yn

        # Insert new application
        application_insert_stmt = """
        INSERT INTO applications (account_id, product_id, standard_yn, amount_requested, special_notes, collateral)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(application_insert_stmt, (
            account_id,
            product_id,
            standard_yn,
            data.amount_requested,
            data.special_notes,
            data.collateral
        ))
        cnx.commit()

        # Get the application ID of the newly inserted record
        cursor.execute("SELECT LAST_INSERT_ID()")
        application_id = cursor.fetchone()[0]

        # Insert new product instance
        product_instance_insert_stmt = """
        INSERT INTO product_instances (application_id, account_id, status_code, latest_note)
        VALUES (%s, %s, 'APL', '')
        """
        cursor.execute(product_instance_insert_stmt, (application_id, account_id))
        cnx.commit()

        # Get the product UID of the newly inserted product instance
        cursor.execute("SELECT LAST_INSERT_ID()")
        product_uid = cursor.fetchone()[0]

        # Send status update email
        m.send_product_status_update_email(product_uid, 'APL')

        return {"status": "Success!", "product_uid": product_uid}

    except Exception as err:
        cnx.rollback()  # Rollback any transaction in case of an error
        raise HTTPException(500, f"An error occurred: {err}")

    finally:
        cursor.close()
        cnx.close()
