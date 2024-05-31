from fastapi import APIRouter, HTTPException, Header, Depends, Request, File, UploadFile
from typing import Annotated, Dict, Set, Any
from dependencies import database as db, helpers as h, schemas as s
import os

router = APIRouter(
    prefix="/my-account",
    tags=["My Account"]
)


@router.get("/{account_id}")
async def get_account_info(account_id: int,
                           token: Annotated[str | None, Header(convert_underscores=False)] = None) -> s.MyAccount:
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(account_id, token):
        raise HTTPException(401, "User is not authorized")

    stmt = "SELECT ac.account_id, ac.first_name, ac.last_name, ac.email, ur.description AS user_role, " \
           "v.description AS verification_status " \
           "FROM accounts ac " \
           "JOIN user_roles ur   ON ac.user_role = ur.role " \
           "JOIN verifications v ON ac.verification = v.verification_status " \
           "WHERE ac.account_id = %s"

    db.cursor.execute(stmt, (account_id, ))
    row_ac = db.cursor.fetchall()[0]

    result = {
        "account_id": row_ac[0],
        "first_name": row_ac[1],
        "last_name": row_ac[2],
        "email": row_ac[3],
        "user_role": row_ac[4],
        "verification_status": row_ac[5]
    }

    return result


@router.put("/{account_id}/password")
async def change_password(account_id: int, credentials: s.Password, token: Annotated[str | None, Header(convert_underscores=False)] = None):
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()
    if not h.verify_authorization(account_id, token):
        raise HTTPException(401, "User is not authorized")

    stmt = "UPDATE login_credentials SET password = %s WHERE account_id = %s"
    db.cursor.execute(stmt, (credentials.password, account_id))
    db.cnx.commit()

    return {"status": "Success!"}


# UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tmp'))
# MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
#
#
# @router.post("/{account_id}/verification-documents")
# async def upload_verification_document(account_id: int, file: UploadFile = File(...),
#                                        token: Annotated[str | None, Header(convert_underscores=False)] = None):
#     if not db.cnx.is_connected():
#         db.cnx, db.cursor = db.connect()
#     if not h.verify_authorization(account_id, token):
#         raise HTTPException(401, "User is not authorized")
#
#     # Check if the file is a PDF
#     if file.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
#
#     # Check if the file size is less than 10MB
#     content = await file.read()
#     if len(content) > MAX_FILE_SIZE:
#         raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
#
#     stmt = "INSERT INTO documents (document_profile) VALUES ('APR')"
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
#     return {"filename": new_file_name}
