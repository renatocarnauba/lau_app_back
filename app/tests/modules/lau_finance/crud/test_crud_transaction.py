import pytest

from app.config.integration import crud
from app.modules.lau_finance.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.tests.modules.lau_finance.faker.fakeTransaction import (
    create_fake_transaction,
    fake_transaction_data,
)
from app.tests.utils.fakeUser import create_fake_user


@pytest.mark.asyncio
@pytest.mark.crud
async def test_create_transaction() -> None:
    transaction_in = TransactionCreate(**await fake_transaction_data())
    user = await create_fake_user()
    transaction = await crud.transaction.create_with_owner(obj_in=transaction_in, owner_id=str(user.id))
    assert transaction.accountId == transaction_in.accountId


@pytest.mark.asyncio
@pytest.mark.crud
async def test_get_transaction() -> None:
    transaction = await create_fake_transaction()
    stored_transaction = await crud.transaction.get(id=transaction.id)
    assert stored_transaction
    assert transaction.id == stored_transaction.id
    assert transaction.accountId == stored_transaction.accountId


@pytest.mark.asyncio
@pytest.mark.crud
async def test_update_transaction() -> None:
    transaction = await create_fake_transaction()
    transaction_update = TransactionUpdate(**await fake_transaction_data())
    transaction2 = await crud.transaction.update(db_obj=transaction, obj_in=transaction_update)
    assert transaction.id == transaction2.id
    assert transaction.accountId != transaction2.accountId
    assert transaction2.accountId == transaction_update.accountId


@pytest.mark.asyncio
@pytest.mark.crud
async def test_delete_transaction() -> None:
    transaction_in_manter = TransactionCreate(**await fake_transaction_data())
    transaction_in_excluir = TransactionCreate(**await fake_transaction_data())
    user = await create_fake_user()
    transactionExcluir = await crud.transaction.create_with_owner(obj_in=transaction_in_excluir, owner_id=str(user.id))
    transactionManter = await crud.transaction.create_with_owner(obj_in=transaction_in_manter, owner_id=str(user.id))
    transactionExcluida = await crud.transaction.remove(id=str(transactionExcluir.id))
    transactionExcluidaAposConsulta = await crud.transaction.get(id=transactionExcluir.id)
    transactionMantidaAposConsulta = await crud.transaction.get(id=transactionManter.id)
    assert transactionExcluidaAposConsulta is None
    assert transactionExcluida is not None
    transactionExcluidaX: Transaction = transactionExcluida
    assert transactionExcluidaX.id == transactionExcluir.id
    assert transactionExcluidaX.accountId == transaction_in_excluir.accountId
    assert transactionMantidaAposConsulta is not None
    transactionMantidaAposConsultaX: Transaction = transactionMantidaAposConsulta
    assert transactionMantidaAposConsultaX.id == transactionManter.id
    assert transactionMantidaAposConsultaX.accountId == transaction_in_manter.accountId
