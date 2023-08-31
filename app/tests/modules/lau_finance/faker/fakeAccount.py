from typing import Any

from faker import Faker
from httpx import AsyncClient

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules.lau_finance.models.account import Account, AccountCreate
from app.tests.utils.fakeUser import create_fake_user

fake = Faker(["pt_BR"])


def fake_account_data() -> dict[str, Any]:
    data = {"name": fake.company(), "is_test": True}
    return data


async def create_fake_account(data: dict[str, Any] | None = None) -> Account:
    if data:
        account_in = AccountCreate(**data)
    else:
        account_in = AccountCreate(**fake_account_data())
    user = await create_fake_user()
    account = await crud.account.create_with_owner(obj_in=account_in, owner_id=str(user.id))
    return account


async def create_fake_account_mine(token: dict[str, Any]) -> Account:
    account_in = AccountCreate(**fake_account_data())
    async with AsyncClient(app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/me", headers=token)
        assert r.status_code == 200
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert "id" in current_user
    account = await crud.account.create_with_owner(obj_in=account_in, owner_id=current_user["id"])
    return account
