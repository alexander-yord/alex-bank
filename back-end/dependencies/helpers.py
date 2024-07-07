from . import database as db
import datetime
import jwt
import configparser, os, sys
from fastapi import HTTPException

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