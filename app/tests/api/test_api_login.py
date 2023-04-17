from typing import Any, Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules.lau_commons.core.exceptions import LoginFail, UserInactive
from app.tests.utils.fakeUser import fake_user_data
from app.tests.utils.utils import check_error_class


@pytest.mark.anyio
async def test_get_access_token() -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        assert r.status_code == 200
        assert "access_token" in tokens
        assert tokens["access_token"]


@pytest.mark.anyio
async def test_get_access_user_invalido() -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER + "x",
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        check_error_class(errorClass=LoginFail, response=r)


@pytest.mark.anyio
async def test_get_access_user_inativo(
    superuser_token_headers: dict[str, Any]
) -> None:
    data = fake_user_data()
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.post(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
            json=data,
        )
        assert 200 <= r.status_code < 300
        created_user = r.json()
        user = await crud.user.get_by_email( email=data["username"])
        assert user
        assert user.email == created_user["email"]
        data["is_active"] = False
        r = await ac.put(
            f"{settings.API_V1_STR}/users/{user.id}",
            headers=superuser_token_headers,
            json=data,
        )
        assert 200 <= r.status_code < 300

    login_data = {
        "username": data["username"],
        "password": data["password"],
    }
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        check_error_class(errorClass=UserInactive, response=r)


@pytest.mark.anyio
async def test_use_access_token(superuser_token_headers: Dict[str, str]) -> None:
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.post(f"{settings.API_V1_STR}/login/test-token", headers=superuser_token_headers)
        result = r.json()
        assert r.status_code == 200
        assert "email" in result
