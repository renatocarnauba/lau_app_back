from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

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
    description: str | None = None
    conciliationDescription: str | None = None
    currencyCode: CurrencyCode = CurrencyCode.BRL
    amount: Decimal = Field(max_digits=5, decimal_places=2, default=0.01)
    category: Optional[str] = None
    type: TransactionType = TransactionType.DEBIT
    efetiveDate: datetime = datetime.now()
    postingDate: datetime = datetime.now()
    conciliateId: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


class TransactionView(Transaction):
    pass


class TransactionUpdate(BaseModel):
    accountId: UUID4
    installmentNumber: Optional[int] = None
    totalInstallments: Optional[int] = None
    description: str | None = None
    conciliationDescription: str | None = None
    currencyCode: CurrencyCode = CurrencyCode.BRL
    amount: Decimal = Field(max_digits=10, decimal_places=2, default=Decimal('0.01'))
    category: Optional[str] = None
    type: TransactionType = TransactionType.DEBIT
    efetiveDate: datetime = datetime.now()
    postingDate: datetime = datetime.now()
    conciliateId: Optional[UUID4] = None


class TransactionCreate(BaseModel):
    is_test: bool = False
    accountId: UUID4
    installmentNumber: Optional[int] = None
    totalInstallments: Optional[int] = None
    description: str | None = None
    conciliationDescription: str | None = None
    currencyCode: CurrencyCode = CurrencyCode.BRL
    amount: Decimal = Field(max_digits=10, decimal_places=2, default=Decimal('0.01'))
    category: Optional[str] = None
    type: TransactionType = TransactionType.DEBIT
    efetiveDate: datetime = datetime.now()
    postingDate: datetime = datetime.now()
    conciliateId: Optional[UUID4] = None
