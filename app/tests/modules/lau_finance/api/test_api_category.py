from typing import Any

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules import lau_finance
from app.modules.lau_commons.core.exceptions import (
    CategoryNotFound,
    UserWithoutPrivileges,
)
from app.tests.modules.lau_finance.faker.fakeCategory import (
    create_fake_category,
    create_fake_category_mine,
    fake_category_data,
)
from app.tests.utils.fakeUser import fake_user_data
from app.tests.utils.utils import (
    check_error_class,
    check_list_in_list,
    compare_two_lists,
    fake_company,
)


class ValueStorage:
    tbCategories: list[dict[str, Any]] = []


@pytest.mark.anyio
async def test_retrieve_category_mine(normaluser_token_headers: dict[str, Any]) -> None:
    tbCategories = []
    for _ in range(5):
        act = await create_fake_category_mine(normaluser_token_headers)
        acctDict = dict(act.__dict__)
        acctDict = jsonable_encoder(acctDict)
        tbCategories.append(acctDict)

    ValueStorage.tbCategories = tbCategories
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/mine", headers=normaluser_token_headers
        )
        assert r.status_code == 200
        tbCategoriesReceived = r.json()

        assert compare_two_lists(tbCategories, tbCategoriesReceived)


@pytest.mark.anyio
async def test_retrieve_category_normaluser(normaluser_token_headers: dict[str, Any]) -> None:
    tbCategories = ValueStorage.tbCategories

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/", headers=normaluser_token_headers
        )
        assert r.status_code == 200
        tbCategoriesReceived = r.json()
        assert compare_two_lists(tbCategories, tbCategoriesReceived)


@pytest.mark.anyio
async def test_retrieve_category_superuser(superuser_token_headers: dict[str, Any]) -> None:
    tbCategories = []
    for _ in range(5):
        act = await create_fake_category_mine(superuser_token_headers)
        acctDict = dict(act.__dict__)
        acctDict = jsonable_encoder(acctDict)
        tbCategories.append(acctDict)

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/", headers=superuser_token_headers)
        assert r.status_code == 200
        tbCategoriesReceived = r.json()
        assert check_list_in_list(tbCategories + ValueStorage.tbCategories, tbCategoriesReceived)


@pytest.mark.anyio
async def test_create_category(normaluser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.post(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/",
            headers=normaluser_token_headers,
            json=fake_category_data(),
        )
        created_user = r.json()
        assert r.status_code == 200
        assert "_id" not in created_user
        assert "id" in created_user


@pytest.mark.anyio
async def test_update_category(superuser_token_headers: dict[str, Any]) -> None:
    data = fake_category_data()
    category = await create_fake_category(data=data)

    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/{category.id}",
            headers=superuser_token_headers,
            json=data,
        )
    assert 200 <= r.status_code < 300
    stored_category = await crud.category.get(id=category.id)
    assert stored_category
    assert stored_category.name == name


@pytest.mark.anyio
async def test_update_category_user_without_privilegies(normaluser_token_headers: dict[str, Any]) -> None:
    data = fake_category_data()
    category = await create_fake_category(data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/{category.id}",
            headers=normaluser_token_headers,
            json=data,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
async def test_update_category_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/0",
            headers=superuser_token_headers,
            json=fake_user_data(),
        )
        check_error_class(errorClass=CategoryNotFound, response=r)


@pytest.mark.anyio
async def test_delete_category(superuser_token_headers: dict[str, Any]) -> None:
    data = fake_category_data()
    category = await create_fake_category(data=data)

    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/{category.id}",
            headers=superuser_token_headers,
        )
    assert 200 <= r.status_code < 300
    stored_category = await crud.category.get(id=category.id)
    assert not stored_category


@pytest.mark.anyio
async def test_delete_category_user_without_privilegies(normaluser_token_headers: dict[str, Any]) -> None:
    data = fake_category_data()
    category = await create_fake_category(data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/{category.id}",
            headers=normaluser_token_headers,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
async def test_delete_category_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/0",
            headers=superuser_token_headers,
        )
        check_error_class(errorClass=CategoryNotFound, response=r)


@pytest.mark.anyio
async def test_get_category(superuser_token_headers: dict[str, Any]) -> None:
    data = fake_category_data()
    category = await create_fake_category(data=data)

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/{category.id}",
            headers=superuser_token_headers,
        )
    assert 200 <= r.status_code < 300
    stored_category = await crud.category.get(id=category.id)
    assert stored_category
    assert stored_category.name == data["name"]
    assert stored_category.id == category.id


@pytest.mark.anyio
async def test_get_category_user_without_privilegies(normaluser_token_headers: dict[str, Any]) -> None:
    data = fake_category_data()
    category = await create_fake_category(data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/{category.id}",
            headers=normaluser_token_headers,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
async def test_get_category_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/categories/0",
            headers=superuser_token_headers,
        )
        check_error_class(errorClass=CategoryNotFound, response=r)
