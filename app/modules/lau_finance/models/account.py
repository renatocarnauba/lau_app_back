from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict

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
    balance: float = 0
    owner_id: str
    conciliateId: Optional[UUID4] = None
    currencyCode: CurrencyCode = CurrencyCode.BRL
    is_active: bool = True
    type: AccountType = AccountType.BANK
    subtype: AccountSubType = AccountSubType.CHECKING_ACCOUNT
    number: Optional[str] = None
    transferNumber: Optional[str] = None
    brand: Optional[str] = None
    level: Optional[str] = None
    billing_cycle: Optional[int] = None
    due_day: Optional[int] = None
    institutionId: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


class AccountView(Account):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None


class AccountCreate(BaseModel):
    name: str
    is_test: bool = False
