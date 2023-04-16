from typing import Any

from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules.lau_finance.models.sql.account import AccountCreate, AccountOrm
from app.tests.utils.fakeUser import create_fake_user

fake = Faker(["pt_BR"])


def fake_account_data() -> dict[str, Any]:
    data = {"name": fake.company()}
    return data


async def create_fake_account(
    asyncSection: async_sessionmaker[AsyncSession], data: dict[str, Any] | None = None
) -> AccountOrm:
    if data:
        account_in = AccountCreate(**data)
    else:
        account_in = AccountCreate(**fake_account_data())
    user = await create_fake_user(asyncSection)
    account = await crud.account.create_with_owner(asyncSection=asyncSection, obj_in=account_in, owner_id=int(user.id))
    return account


async def create_fake_account_mine(asyncSection: async_sessionmaker[AsyncSession], token: dict[str, Any]) -> AccountOrm:
    account_in = AccountCreate(**fake_account_data())
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/me", headers=token)
        assert r.status_code == 200
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert "id" in current_user
    account = await crud.account.create_with_owner(
        asyncSection=asyncSection, obj_in=account_in, owner_id=current_user["id"]
    )
    return account
