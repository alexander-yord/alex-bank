from . import database as db
import datetime
import jwt
import configparser, os, sys
from fastapi import HTTPException
from . import schemas as s

cursor = db.cursor
cnx = db.cnx

try:
    cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
    cfile.read(os.path.join(sys.path[0], "config.ini"))

    SECRET_KEY = cfile["ENCRYPT"]["SECRET_KEY"]
except FileNotFoundError as err:
    SECRET_KEY = None
    print(err)


def create_jwt_token(account_id: int, user_role: str, exp: int = 7200) -> str:
    """
    Create a JWT token.

    Parameters:
    - account_id (int): The account ID.
    - user_role (str): The user role.
    - exp (int, optional): The expiration time in seconds. Default is 7200 seconds (2 hours).

    Returns:
    - str: The JWT token.
    """

    # Define the payload
    payload = {
        'account_id': account_id,
        'user_role': user_role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=exp)
    }

    # Create the JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return token


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload.get("account_id"), payload.get("user_role")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verification_emoji(verification_status):
    emojis = {
        "Y": "✅",
        "N": "🟡",
        "C": "📩",
        "R": "🚫"
    }
    return emojis.get(verification_status)


def available_next_status(current_status: str):
    global cnx, cursor
    if not cnx.is_connected():
        cnx, cursor = db.connect()

    cursor.execute("SELECT code, call_to_action, status_description FROM product_statuses")
    res = cursor.fetchall()

    statuses = {status[0]: {"status_code": status[0], "status_name": status[1], "status_description": status[2]}
                for status in res}

    if current_status not in statuses:
        return "XXX"

    next_status_map = {
        "APL": ["REV", "APR", "DEN", "AMD", "CNL"],
        "REV": ["APR", "DEN", "AMD", "CNL"],
        "AMD": ["AGR", "DIS", "CNL"],
        "AGR": ["APR", "CNL"],
        "DIS": ["AMD", "CNL"],
        "APR": ["SGN", "CNL"],
        "SGN": ["AWT", "CNL"],
        "AWT": ["NOR", "CNL"],
        "NOR": ["TRG", "DUE"],
        "TRG": ["DUE"],
        "DUE": ["CMP", "ORD"],
        "ORD": ["CMP", "WOF"],
        "CNL": [],
        "CMP": [],
        "WOF": []
    }

    next_statuses = next_status_map.get(current_status, [])
    return [statuses[key] for key in next_statuses if key in statuses]


def status_progressions(current_status: str):
    global cnx, cursor
    if not cnx.is_connected():
        cnx, cursor = db.connect()

    cursor.execute("SELECT code, status_name, status_description FROM product_statuses")
    res = cursor.fetchall()

    statuses = {status[0]: {"status_name": status[1], "status_description": status[2]} for status in res}

    if current_status not in statuses:
        return "XXX"

    next_status_map = {
        "APL": ["REV", "APR", "SGN", "AWT", "NOR", "DUE", "CMP"],
        "REV": ["APR", "SGN", "AWT", "NOR", "DUE", "CMP"],
        "AMD": ["AGR", "APR", "SGN", "AWT", "NOR", "DUE", "CMP"],
        "AGR": ["APR", "SGN", "AWT", "NOR", "DUE", "CMP"],
        "DIS": ["AMD", "AGR", "APR", "SGN", "AWT", "NOR", "DUE", "CMP"],
        "APR": ["SGN", "AWT", "NOR", "DUE", "CMP"],
        "SGN": ["AWT", "NOR", "DUE", "CMP"],
        "AWT": ["NOR", "DUE", "CMP"],
        "NOR": ["DUE", "CMP"],
        "TRG": ["DUE", "CMP"],
        "DUE": ["CMP"],
        "ORD": ["CMP"],
        "CNL": [],
        "CMP": [],
        "WOF": []
    }

    next_statuses = next_status_map.get(current_status, [])
    return [statuses[key] for key in next_statuses if key in statuses]


def update_product_custom_fields(custom_column: s.ProductCustomColumns, is_client=True):
    global cnx, cursor
    if not cnx.is_connected():
        cnx, cursor = db.connect()

    stmt = """SELECT pccd.column_type, pccd.customer_visible_yn FROM product_custom_column_values pccv
    JOIN product_custom_column_def pccd ON pccd.pcc_id = pccv.pcc_id WHERE pccv.pcc_uid = %s"""
    cursor.execute(stmt, (custom_column.pcc_uid,))

    if cursor.rowcount == 0:
        raise HTTPException(404, "Product custom column not found")
    row = cursor.fetchone()

    column_name = ""
    value = None
    if row[1] == "Y" or not is_client:
        if row[0] == "integer":
            column_name = 'int_value'
            value = custom_column.int_value
        elif row[0] == "float":
            column_name = "float_value"
            value = custom_column.float_value
        elif row[0] == "varchar":
            column_name = "varchar_value"
            value = custom_column.varchar_value
        elif row[0] == "text":
            column_name = "text_value"
            value = custom_column.text_value
        elif row[0] == "date":
            column_name = "date_value"
            value = custom_column.date_value
        elif row[0] == "datetime":
            column_name = "datetime_value"
            value = custom_column.datetime_value

        # Prepare the SQL query with proper handling of None
        if value is None:
            sql = f"UPDATE product_custom_column_values SET {column_name} = NULL WHERE pcc_uid = %s"
            cursor.execute(sql, (custom_column.pcc_uid,))
        else:
            sql = f"UPDATE product_custom_column_values SET {column_name} = %s WHERE pcc_uid = %s"
            cursor.execute(sql, (value, custom_column.pcc_uid))

        cnx.commit()
    else:
        raise HTTPException(401, "User is not authorized to change this field.")

    return
