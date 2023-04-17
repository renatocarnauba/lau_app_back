from pprint import pprint
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from fastapi.encoders import jsonable_encoder

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules import lau_finance
from app.modules.lau_commons.core.exceptions import (
    AccountNotFound,
    UserWithoutPrivileges,
)
from app.tests.modules.lau_finance.faker.fakeAccount import (
    create_fake_account,
    create_fake_account_mine,
    fake_account_data,
)
from app.tests.utils.fakeUser import fake_user_data
from app.tests.utils.utils import (
    check_error_class,
    check_list_in_list,
    compare_two_lists,
    fake_company,
)


class ValueStorage:
    tbAccounts: list[dict[str, Any]] = []


@pytest.mark.anyio
async def test_retrieve_account_mine(
    normaluser_token_headers: dict[str, Any]
) -> None:
    tbAccounts = []
    for _ in range(5):
        act = await create_fake_account_mine( normaluser_token_headers)
        acctDict = dict(act.__dict__)
        acctDict = jsonable_encoder(acctDict)
        tbAccounts.append(acctDict)

    ValueStorage.tbAccounts = tbAccounts
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/mine", headers=normaluser_token_headers
        )
        assert r.status_code == 200
        tbAccountsReceived = r.json()

        assert compare_two_lists(tbAccounts, tbAccountsReceived)


@pytest.mark.anyio
async def test_retrieve_account_normaluser(normaluser_token_headers: dict[str, Any]) -> None:
    tbAccounts = ValueStorage.tbAccounts

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/", headers=normaluser_token_headers)
        assert r.status_code == 200
        tbAccountsReceived = r.json()
        assert compare_two_lists(tbAccounts, tbAccountsReceived)


@pytest.mark.anyio
async def test_retrieve_account_superuser(
    superuser_token_headers: dict[str, Any]
) -> None:
    tbAccounts = []
    for _ in range(5):
        act = await create_fake_account_mine( superuser_token_headers)
        acctDict = dict(act.__dict__)
        acctDict = jsonable_encoder(acctDict)
        tbAccounts.append(acctDict)

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/", headers=superuser_token_headers)
        assert r.status_code == 200
        tbAccountsReceived = r.json()
        assert check_list_in_list(tbAccounts + ValueStorage.tbAccounts, tbAccountsReceived)


@pytest.mark.anyio
async def test_create_account(normaluser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.post(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/",
            headers=normaluser_token_headers,
            json=fake_account_data(),
        )
        created_user = r.json()
        assert r.status_code == 200
        assert "_id" not in created_user
        assert "id" in created_user


@pytest.mark.anyio
async def test_update_account(
    superuser_token_headers: dict[str, Any]
) -> None:
    data = fake_account_data()
    account = await create_fake_account( data=data)

    name = fake_company()
    data["name"] = name

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/{account.id}",
            headers=superuser_token_headers,
            json=data,
        )
    assert 200 <= r.status_code < 300
    stored_account = await crud.account.get( id=account.id)
    assert stored_account
    assert stored_account.name == name


@pytest.mark.anyio
async def test_update_account_user_without_privilegies(
    normaluser_token_headers: dict[str, Any]
) -> None:
    data = fake_account_data()
    account = await create_fake_account( data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/{account.id}",
            headers=normaluser_token_headers,
            json=data,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
async def test_update_account_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/0",
            headers=superuser_token_headers,
            json=fake_user_data(),
        )
        check_error_class(errorClass=AccountNotFound, response=r)


@pytest.mark.anyio
async def test_delete_account(
    superuser_token_headers: dict[str, Any]
) -> None:
    data = fake_account_data()
    account = await create_fake_account( data=data)

    name = fake_company()
    data["name"] = name

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/{account.id}",
            headers=superuser_token_headers,
        )
    assert 200 <= r.status_code < 300
    stored_account = await crud.account.get( id=account.id)
    assert not stored_account


@pytest.mark.anyio
async def test_delete_account_user_without_privilegies(
    normaluser_token_headers: dict[str, Any]
) -> None:
    data = fake_account_data()
    account = await create_fake_account( data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/{account.id}",
            headers=normaluser_token_headers,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
async def test_delete_account_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/0",
            headers=superuser_token_headers,
        )
        check_error_class(errorClass=AccountNotFound, response=r)


@pytest.mark.anyio
async def test_get_account(
    superuser_token_headers: dict[str, Any]
) -> None:
    data = fake_account_data()
    account = await create_fake_account( data=data)

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/{account.id}",
            headers=superuser_token_headers,
        )
    assert 200 <= r.status_code < 300
    stored_account = await crud.account.get( id=account.id)
    assert stored_account
    assert stored_account.name == data["name"]
    assert stored_account.id == account.id


@pytest.mark.anyio
async def test_get_account_user_without_privilegies(
    normaluser_token_headers: dict[str, Any]
) -> None:
    data = fake_account_data()
    account = await create_fake_account( data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/{account.id}",
            headers=normaluser_token_headers,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
async def test_get_account_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/accounts/0",
            headers=superuser_token_headers,
        )
        check_error_class(errorClass=AccountNotFound, response=r)
