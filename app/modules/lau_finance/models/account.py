from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel

from app.modules.lau_commons.models.baseModel import ModelTemplate


class AccountType(str, Enum):
    BANK = "BANK"
    CREDIT = "CREDIT"


class AccountSubType(str, Enum):
    CHECKING_ACCOUNT = "CHECKING_ACCOUNT"
    CREDIT_CARD = "CREDIT_CARD"
    SAVINGS_ACCOUNT = "SAVINGS_ACCOUNT"


class CurrencyCode(str, Enum):
    BRL = "BRL"
    USD = "USD"


class Account(ModelTemplate):
    __tablename__ = "fin_account"
    name: str
    balance: float
    owner_id: str
    conciliateId: Optional[UUID4]
    currencyCode: CurrencyCode
    is_active: bool = True
    type: AccountType
    subtype: AccountSubType
    number: Optional[str]
    transferNumber: Optional[str]
    brand: Optional[str]
    level: Optional[str]
    billing_cycle: Optional[int]
    due_day: Optional[int]
    institutionId: UUID4

    class Config:
        orm_mode = True


class AccountView(Account):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None


class AccountCreate(BaseModel):
    name: str
    is_test: bool = False
