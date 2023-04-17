import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.config.integration import crud
from app.modules.lau_finance.models.account import (
    AccountCreate,
    AccountOrm,
    AccountUpdate,
)
from app.tests.modules.lau_finance.faker.fakeAccount import (
    create_fake_account,
    fake_account_data,
)
from app.tests.utils.fakeUser import create_fake_user


@pytest.mark.asyncio
async def test_create_account() -> None:
    account_in = AccountCreate(**fake_account_data())
    user = await create_fake_user()
    account = await crud.account.create_with_owner( obj_in=account_in, owner_id=int(user.id))
    assert account.name == account_in.name
    assert account.owner_id == user.id


@pytest.mark.asyncio
async def test_get_account() -> None:
    account = await create_fake_account()
    stored_account = await crud.account.get( id=account.id)
    assert stored_account
    assert account.id == stored_account.id
    assert account.name == stored_account.name
    assert account.owner_id == stored_account.owner_id


@pytest.mark.asyncio
async def test_update_account() -> None:
    account = await create_fake_account()
    account_update = AccountUpdate(**fake_account_data())
    account2 = await crud.account.update( db_obj=account, obj_in=account_update)
    assert account.id == account2.id
    assert account.name == account2.name
    assert account2.name == account_update.name
    assert account.owner_id == account2.owner_id


@pytest.mark.asyncio
async def test_delete_account() -> None:
    account_in_manter = AccountCreate(**fake_account_data())
    account_in_excluir = AccountCreate(**fake_account_data())
    user = await create_fake_user()
    accountExcluir = await crud.account.create_with_owner(
         obj_in=account_in_excluir, owner_id=int(user.id)
    )
    accountManter = await crud.account.create_with_owner(
         obj_in=account_in_manter, owner_id=int(user.id)
    )
    accountExcluida = await crud.account.remove( id=int(accountExcluir.id))
    accountExcluidaAposConsulta = await crud.account.get( id=accountExcluir.id)
    accountMantidaAposConsulta = await crud.account.get( id=accountManter.id)
    assert accountExcluidaAposConsulta is None
    assert accountExcluida is not None
    accountExcluidaX: AccountOrm = accountExcluida
    assert accountExcluidaX.id == accountExcluir.id
    assert accountExcluidaX.name == account_in_excluir.name
    assert accountExcluidaX.owner_id == user.id
    assert accountMantidaAposConsulta is not None
    accountMantidaAposConsultaX: AccountOrm = accountMantidaAposConsulta
    assert accountMantidaAposConsultaX.id == accountManter.id
    assert accountMantidaAposConsultaX.name == account_in_manter.name
    assert accountMantidaAposConsultaX.owner_id == user.id
