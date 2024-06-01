from pydantic import BaseModel
from typing import Optional


class LoggedInUser(BaseModel):
    account_id: int
    first_name: str
    last_name:  str
    user_role:  str
    token:      str


class MyAccount(BaseModel):
    account_id: int
    first_name: str
    last_name:  str
    email:      str
    user_role:  str
    verification_status: str


class Password(BaseModel):
    password: str


class NewAccount(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    country: str
    address: Optional[str] = None
    password: str

