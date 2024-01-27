from typing import Any

from faker import Faker
from httpx import AsyncClient

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules.lau_finance.models.transaction import Transaction, TransactionCreate
from app.tests.modules.lau_finance.faker.fakeAccount import create_fake_account
from app.tests.utils.fakeUser import create_fake_user

fake = Faker(["pt_BR"])


async def fake_transaction_data() -> dict[str, Any]:
    account=await create_fake_account()
    data = {"is_test": True, "accountId":account.id}
    return data


async def create_fake_transaction(data: dict[str, Any] | None = None) -> Transaction:
    if data:
        transaction_in = TransactionCreate(**data)
    else:
        transaction_in = TransactionCreate(**await fake_transaction_data())
    user = await create_fake_user()
    transaction = await crud.transaction.create_with_owner(obj_in=transaction_in, owner_id=str(user.id))
    return transaction


async def create_fake_transaction_mine(token: dict[str, Any]) -> Transaction:
    transaction_in = TransactionCreate(**await fake_transaction_data())
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/me", headers=token)
        assert r.status_code == 200
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert "id" in current_user
    transaction = await crud.transaction.create_with_owner(obj_in=transaction_in, owner_id=current_user["id"])
    return transaction
