from app.modules.lau_commons.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_finance.models.account import (
    AccountCreate,
    AccountOrm,
    AccountUpdate,
)


class CRUDAccount(CRUDBaseMultiAsync[AccountOrm, AccountCreate, AccountUpdate]):
    ...


account = CRUDAccount(AccountOrm)
