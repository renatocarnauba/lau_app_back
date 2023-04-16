from typing import Any

from faker import Faker
from httpx import AsyncClient
from odmantic import AIOEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules.lau_finance.models.nosql.category import CategoryCreate, CategoryOrm
from app.tests.utils.fakeUser import create_fake_user

fake = Faker(["pt_BR"])


def fake_category_data() -> dict[str, Any]:
    data = {"name": fake.company()}
    return data


async def create_fake_category(
    asyncSection: async_sessionmaker[AsyncSession], asyncSectionMongo: AIOEngine, data: dict[str, Any] | None = None
) -> CategoryOrm:
    if data:
        category_in = CategoryCreate(**data)
    else:
        category_in = CategoryCreate(**fake_category_data())
    user = await create_fake_user(asyncSection)
    category = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in, owner_id=int(user.id)
    )
    return category


async def create_fake_category_mine(
    asyncSectionMongo: AIOEngine, token: dict[str, Any]
) -> CategoryOrm:
    category_in = CategoryCreate(**fake_category_data())
    async with AsyncClient(app=app, base_url=f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/") as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/me", headers=token)
        assert r.status_code == 200
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert "id" in current_user
    category = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in, owner_id=current_user["id"]
    )
    return category
