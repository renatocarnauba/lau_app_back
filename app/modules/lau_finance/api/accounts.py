from typing import Any, List

from fastapi import APIRouter, Depends

from app.api import depsAsync
from app.config.integration import crud, models
from app.modules.lau_commons.core.exceptions import (
    AccountNotFound,
    UserWithoutPrivileges,
)
from app.modules.lau_finance.models.account import (
    AccountCreate,
    Account,
    AccountUpdate,
    AccountView,
)

router = APIRouter()


@router.get("/mine", response_model=List[AccountView])
async def read_accounts_mine(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve accounts Mine.
    """
    accounts = await crud.account.get_multi_by_owner(owner_id=str(current_user.id), skip=skip, limit=limit)
    return accounts


@router.get("/", response_model=List[AccountView])
async def read_accounts(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve accounts.
    """
    if crud.user.is_superuser(current_user):
        accounts = await crud.account.get_multi(skip=skip, limit=limit)
    else:
        accounts = await crud.account.get_multi_by_owner(owner_id=str(current_user.id), skip=skip, limit=limit)
    return accounts


@router.post("/", response_model=AccountView)
async def create_account(
    *,
    account_in: AccountCreate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Create new account.
    """
    account: Account = await crud.account.create_with_owner(obj_in=account_in, owner_id=str(current_user.id))
    return account


@router.put("/{id}", response_model=AccountView)
async def update_account(
    *,
    id: str,
    account_in: AccountUpdate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Update an account.
    """
    account = await crud.account.get(id=id)
    if not account:
        raise AccountNotFound()
    if not crud.user.is_superuser(current_user) and (account.owner_id != current_user.id):
        raise UserWithoutPrivileges()

    account = await crud.account.update(db_obj=account, obj_in=account_in)
    return account


@router.get("/{id}", response_model=AccountView)
async def read_account(
    *,
    id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get account by ID.
    """
    account = await crud.account.get(id=id)
    if not account:
        raise AccountNotFound()
    if not crud.user.is_superuser(current_user) and (account.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    return account


@router.delete("/{id}", response_model=AccountView)
async def delete_account(
    *,
    id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Delete an account.
    """
    account = await crud.account.get(id=id)
    if not account:
        raise AccountNotFound()
    if not crud.user.is_superuser(current_user) and (account.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    account = await crud.account.remove(id=id)
    return account
