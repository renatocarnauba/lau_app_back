from app.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_finance.models.sql.account import (
    AccountCreate,
    AccountOrm,
    AccountUpdate,
)


class CRUDAccount(CRUDBaseMultiAsync[AccountOrm, AccountCreate, AccountUpdate]):
    ...


account = CRUDAccount(AccountOrm)
