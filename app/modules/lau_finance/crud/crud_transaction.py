from app.modules.lau_commons.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_finance.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
)


class CRUDTransaction(CRUDBaseMultiAsync[Transaction, TransactionCreate, TransactionUpdate]):
    ...


transaction = CRUDTransaction(Transaction)
