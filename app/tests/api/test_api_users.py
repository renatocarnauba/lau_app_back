from typing import Any, Dict

import pytest
from httpx import AsyncClient

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules.lau_commons.core.exceptions import (
    UserAlreadyExists,
    UserNotFound,
    UserWithoutPrivileges,
)
from app.tests.utils.fakeUser import create_fake_user, fake_user_data
from app.tests.utils.utils import check_error_class


@pytest.mark.anyio
async def test_get_users_me_superuser(superuser_token_headers: Dict[str, str]) -> None:
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert current_user["is_superuser"]


@pytest.mark.anyio
async def test_get_existing_user(
    superuser_token_headers: dict[str, Any]
) -> None:
    user = await create_fake_user()
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/{user.id}", headers=superuser_token_headers)
        assert 200 <= r.status_code < 300
        api_user = r.json()
        existing_user = await crud.user.get_by_email( email=str(user.email))
        assert existing_user
        assert existing_user.email == api_user["email"]


@pytest.mark.anyio
async def test_get_existing_user_me(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert current_user["is_superuser"]
        assert "id" in current_user
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        current_id = current_user["id"]
        r = await ac.get(f"{settings.API_V1_STR}/users/{current_id}", headers=superuser_token_headers)
        assert 200 <= r.status_code < 300
        api_user = r.json()
        assert api_user["id"] == current_id


@pytest.mark.anyio
async def test_get_existing_user_when_not_superuser(
    normaluser_token_headers: dict[str, Any]
) -> None:
    user = await create_fake_user()

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/{user.id}", headers=normaluser_token_headers)
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
async def test_create_user_existing_username(
    superuser_token_headers: dict[str, Any]
) -> None:
    userData = fake_user_data()
    await create_fake_user( data=userData)

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.post(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=userData)
        check_error_class(errorClass=UserAlreadyExists, response=r)
        created_user = r.json()
        assert "_id" not in created_user


@pytest.mark.anyio
async def test_retrieve_users(
    superuser_token_headers: dict[str, Any]
) -> None:
    await create_fake_user()
    await create_fake_user()

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
        all_users = r.json()
        assert len(all_users) > 1
        for item in all_users:
            assert "email" in item


@pytest.mark.anyio
async def test_update_user(
    superuser_token_headers: dict[str, Any]
) -> None:
    data = fake_user_data()
    user = await create_fake_user( data=data)

    data["is_active"] = False

    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/users/{user.id}",
            headers=superuser_token_headers,
            json=data,
        )
    assert 200 <= r.status_code < 300
    userRetrieved = await crud.user.get_by_email( email=data["email"])
    assert userRetrieved
    assert not userRetrieved.is_active


@pytest.mark.anyio
async def test_update_user_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/users/0",
            headers=superuser_token_headers,
            json=fake_user_data(),
        )
        check_error_class(errorClass=UserNotFound, response=r)
