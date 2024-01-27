from typing import Any

from faker import Faker
from httpx import AsyncClient

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules.lau_finance.models.institution import Institution, InstitutionCreate
from app.tests.utils.fakeUser import create_fake_user

fake = Faker(["pt_BR"])


def fake_institution_data() -> dict[str, Any]:
    data = {"name": fake.company(), "is_test": True}
    return data


async def create_fake_institution(data: dict[str, Any] | None = None) -> Institution:
    if data:
        institution_in = InstitutionCreate(**data)
    else:
        institution_in = InstitutionCreate(**fake_institution_data())
    user = await create_fake_user()
    institution = await crud.institution.create_with_owner(obj_in=institution_in, owner_id=str(user.id))
    return institution


async def create_fake_institution_mine(token: dict[str, Any]) -> Institution:
    institution_in = InstitutionCreate(**fake_institution_data())
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(f"{settings.API_V1_STR}/users/me", headers=token)
        assert r.status_code == 200
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert "id" in current_user
    institution = await crud.institution.create_with_owner(obj_in=institution_in, owner_id=current_user["id"])
    return institution
