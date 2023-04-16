from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.api import depsAsync
from app.config.integration import crud, models
from app.core.exceptions import AccountNotFound, UserWithoutPrivileges
from app.modules.lau_finance.models.sql.account import (
    AccountCreate,
    AccountOrm,
    AccountUpdate,
    AccountView,
)

router = APIRouter()


@router.get("/mine", response_model=List[AccountView])
async def read_accounts_mine(
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve accounts Mine.
    """
    accounts = await crud.account.get_multi_by_owner(
        asyncSection=asyncSection, owner_id=int(current_user.id), skip=skip, limit=limit
    )
    return accounts


@router.get("/", response_model=List[AccountView])
async def read_accounts(
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve accounts.
    """
    if crud.user.is_superuser(current_user):
        accounts = await crud.account.get_multi(asyncSection=asyncSection, skip=skip, limit=limit)
    else:
        accounts = await crud.account.get_multi_by_owner(
            asyncSection=asyncSection, owner_id=int(current_user.id), skip=skip, limit=limit
        )
    return accounts


@router.post("/", response_model=AccountView)
async def create_account(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    account_in: AccountCreate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Create new account.
    """
    account: AccountOrm = await crud.account.create_with_owner(
        asyncSection=asyncSection, obj_in=account_in, owner_id=int(current_user.id)
    )
    return account


@router.put("/{id}", response_model=AccountView)
async def update_account(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    id: int,
    account_in: AccountUpdate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Update an account.
    """
    account = await crud.account.get(asyncSection=asyncSection, id=id)
    if not account:
        raise AccountNotFound()
    if not crud.user.is_superuser(current_user) and (account.owner_id != current_user.id):
        raise UserWithoutPrivileges()

    account = await crud.account.update(asyncSection=asyncSection, db_obj=account, obj_in=account_in)
    return account


@router.get("/{id}", response_model=AccountView)
async def read_account(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    id: int,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get account by ID.
    """
    account = await crud.account.get(asyncSection=asyncSection, id=id)
    if not account:
        raise AccountNotFound()
    if not crud.user.is_superuser(current_user) and (account.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    return account


@router.delete("/{id}", response_model=AccountView)
async def delete_account(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    id: int,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Delete an account.
    """
    account = await crud.account.get(asyncSection=asyncSection, id=id)
    if not account:
        raise AccountNotFound()
    if not crud.user.is_superuser(current_user) and (account.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    account = await crud.account.remove(asyncSection=asyncSection, id=id)
    return account
