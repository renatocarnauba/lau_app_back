from typing import Any, List

from fastapi import APIRouter, Depends

from app.api import depsAsync
from app.config.integration import crud, models
from app.modules.lau_commons.core.exceptions import (
    TransactionNotFound,
    UserWithoutPrivileges,
)
from app.modules.lau_finance.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    TransactionView,
)

router = APIRouter()


@router.get("/mine", response_model=List[TransactionView])
async def read_transactions_mine(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve transactions Mine.
    """
    transactions = await crud.transaction.get_multi_by_owner(owner_id=str(current_user.id), skip=skip, limit=limit)
    return transactions


@router.get("/", response_model=List[TransactionView])
async def read_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve transactions.
    """
    if crud.user.is_superuser(current_user):
        transactions = await crud.transaction.get_multi(skip=skip, limit=limit)
    else:
        transactions = await crud.transaction.get_multi_by_owner(owner_id=str(current_user.id), skip=skip, limit=limit)
    return transactions


@router.post("/", response_model=TransactionView)
async def create_transaction(
    *,
    transaction_in: TransactionCreate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Create new transaction.
    """
    transaction: Transaction = await crud.transaction.create_with_owner(
        obj_in=transaction_in, owner_id=str(current_user.id)
    )
    return transaction


@router.put("/{id}", response_model=TransactionView)
async def update_transaction(
    *,
    id: str,
    transaction_in: TransactionUpdate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Update an transaction.
    """
    transaction = await crud.transaction.get(id=id)
    if not transaction:
        raise TransactionNotFound()
    if not crud.user.is_superuser(current_user) and (transaction.owner_id != current_user.id):
        raise UserWithoutPrivileges()

    transaction = await crud.transaction.update(db_obj=transaction, obj_in=transaction_in)
    return transaction


@router.get("/{id}", response_model=TransactionView)
async def read_transaction(
    *,
    id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get transaction by ID.
    """
    transaction = await crud.transaction.get(id=id)
    if not transaction:
        raise TransactionNotFound()
    if not crud.user.is_superuser(current_user) and (transaction.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    return transaction


@router.delete("/{id}", response_model=TransactionView)
async def delete_transaction(
    *,
    id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Delete an transaction.
    """
    transaction = await crud.transaction.get(id=id)
    if not transaction:
        raise TransactionNotFound()
    if not crud.user.is_superuser(current_user) and (transaction.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    transaction = await crud.transaction.remove(id=id)
    return transaction
