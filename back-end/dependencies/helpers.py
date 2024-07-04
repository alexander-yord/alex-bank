from . import database as db
import random
import string

cursor = db.cursor
cnx = db.cnx
CHARACTERS = string.ascii_letters + string.digits


def generate_authorization(length=512):  # generates the authorization token
    return ''.join(random.choice(CHARACTERS) for i in range(length))


def verify_authorization(account_id, authorization):  # verifies that the token passed is the correct one
    global cnx, cursor
    if not cnx.is_connected():
        cnx, cursor = db.connect()
    stmt = "SELECT account_id FROM login_sessions WHERE token = %s "
    cursor.execute(stmt, (authorization,))
    if cursor.rowcount == 0:
        return False
    row = cursor.fetchall()[0]
    return True if row[0] == account_id else False


# def check_user_privilege(account_id, roles: list):
#     global cnx, cursor
#     if not cnx.is_connected():
#         cnx, cursor = db.connect()
#     cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s AND user_role IN (%s)",
#                    (account_id, roles))
#     return True if cursor.rowcount == 1 else False

def check_user_privilege(account_id, roles: list):
    global cnx, cursor
    if not cnx.is_connected():
        cnx, cursor = db.connect()

    # Construct the placeholders for the roles
    placeholders = ', '.join(['%s'] * len(roles))

    # Construct the SQL query
    query = f"SELECT account_id FROM accounts WHERE account_id = %s AND user_role IN ({placeholders})"

    # Execute the query with account_id and roles expanded into parameters
    cursor.execute(query, (account_id, *roles))

    return cursor.rowcount == 1


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