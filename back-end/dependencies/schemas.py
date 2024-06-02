from pydantic import BaseModel
from typing import Optional, List
from fastapi import Query


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


class UserRole(BaseModel):
    role: str
    description: str


class Verification(BaseModel):
    status_code: str
    verification_status: str


class AccountGroup(BaseModel):
    group_name: str
    group_code: str
    group_description: str
    default_yn: str


class DropDownOptions(BaseModel):
    user_role: List[UserRole]
    verifications: List[Verification]
    account_groups: List[AccountGroup]


class BroadAccountFilters(BaseModel):
    country_code: Optional[List[str]] = Query(None)
    user_role: Optional[List[str]] = Query(None)
    verification: Optional[List[str]] = Query(None)
    account_group: Optional[List[str]] = Query(None)
