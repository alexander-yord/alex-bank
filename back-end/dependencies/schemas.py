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


class UpdateNoteModel(BaseModel):
    content: Optional[str] = None
    public_yn: Optional[str] = None


class AmendAccount(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    country_code: Optional[str] = None
    address: Optional[str] = None


class AmendAccountGroup(BaseModel):
    account_group_code: str


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


class Statuses(BaseModel):
    status_code: str
    status_name: str
    call_to_action: Optional[str] = None
    status_description: str
    show: bool


class DropDownOptions(BaseModel):
    user_role: List[UserRole]
    verifications: List[Verification]
    account_groups: List[AccountGroup]
    statuses: List[Statuses]


class BroadAccountFilters(BaseModel):
    country_code: Optional[List[str]] = Query(None)
    user_role: Optional[List[str]] = Query(None)
    verification: Optional[List[str]] = Query(None)
    account_group: Optional[List[str]] = Query(None)


class Product(BaseModel):
    product_id: int
    category_id: str
    category_name: str
    name: str
    description: str
    terms_and_conditions: Optional[str] = None
    currency: Optional[str] = None
    term: Optional[int] = None
    percentage: Optional[float] = None
    monetary_amount: Optional[float] = None
    percentage_label: Optional[str] = None
    mon_amt_label: Optional[str] = None
    available_from: Optional[str] = None
    available_till: Optional[str] = None


class ProductCategory(BaseModel):
    category_id: str
    category_name: str
    category_description: str


class NewProduct(BaseModel):
    amount_requested: float
    collateral: Optional[str] = None
    standard_yn: str
    special_notes: Optional[str] = None


class StatusUpdates(BaseModel):
    status_code: str
    status_name: str
    status_description: str
    update_user: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status_update_dt: str
    update_note: Optional[str] = None
    public_yn: Optional[str] = None


class ProductInstancePublic(BaseModel):
    product_uid: int
    account_id: int
    statuses: List[StatusUpdates]
    product_id: int
    amount: Optional[float] = None
    contract_id: Optional[int] = None
    product_start_date: Optional[str] = None
    product_end_date: Optional[str] = None
    actual_end_date: Optional[str] = None
    special_notes: Optional[str] = None
    application_id: int
    approved_by: Optional[int] = None
    amount_requested: float
    appl_special_notes: Optional[str] = None
    collateral: Optional[str] = None
    approved_yn: Optional[str] = None
    approval_dt: Optional[str] = None
    yield_: Optional[float] = 0
    standard: str
    notifications: str


class ProductInstancePrivate(BaseModel):
    product_uid: int
    account_id: int
    statuses: List[StatusUpdates]
    product_id: int
    amount: Optional[float] = None
    contract_id: Optional[int] = None
    product_start_date: Optional[str] = None
    product_end_date: Optional[str] = None
    actual_end_date: Optional[str] = None
    special_notes: Optional[str] = None
    application_id: int
    approved_by: Optional[int] = None
    amount_requested: float
    appl_special_notes: Optional[str] = None
    collateral: Optional[str] = None
    approved_yn: Optional[str] = None
    approval_dt: Optional[str] = None
    yield_: Optional[float] = 0
    actual_revenue: Optional[float] = None
    expected_revenue: Optional[float] = None
    standard: str
    notifications: str


class AmendProductInstance(BaseModel):
    amount: Optional[float] = None
    yield_: Optional[float] = None  # 'yield' is a reserved keyword in Python, hence the underscore
    contract_id: Optional[int] = None
    expected_revenue: Optional[float] = None
    product_start_date: Optional[str] = None
    product_end_date: Optional[str] = None
    special_notes: Optional[str] = None
    actual_end_date: Optional[str] = None
    actual_revenue: Optional[float] = None


class ProductCard(BaseModel):
    product_uid: int
    application_id: int
    contract_id: Optional[int] = None
    approved_by: Optional[int] = None
    name: str
    description: str
    amount: float
    status_code: str
    status_name: str
    category_id: str
    currency: str


