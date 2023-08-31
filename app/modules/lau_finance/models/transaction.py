from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict

from app.modules.lau_commons.models.baseModel import ModelTemplate
from app.modules.lau_finance.models.account import CurrencyCode


class TransactionType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class TransactionSubType(str, Enum):
    CHECKING_ACCOUNT = "CHECKING_ACCOUNT"
    CREDIT_CARD = "CREDIT_CARD"
    SAVINGS_ACCOUNT = "SAVINGS_ACCOUNT"


class Transaction(ModelTemplate):
    __tablename__ = "fin_transaction"

    is_active: bool = True
    accountId: UUID4
    installmentNumber: Optional[int] = None
    totalInstallments: Optional[int] = None
    description: str
    conciliationDescription: str
    currencyCode: CurrencyCode
    amount: float
    category: Optional[str] = None
    type: TransactionType
    efetiveDate: datetime
    postingDate: datetime
    conciliateId: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


class TransactionView(Transaction):
    pass


class TransactionUpdate(BaseModel):
    name: Optional[str] = None


class TransactionCreate(BaseModel):
    name: str
    is_test: bool = False
