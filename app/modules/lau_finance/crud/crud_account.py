from app.modules.lau_commons.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_finance.models.account import (
    AccountCreate,
    Account,
    AccountUpdate,
)


class CRUDAccount(CRUDBaseMultiAsync[Account, AccountCreate, AccountUpdate]):
    ...


account = CRUDAccount(Account)
