from typing import Any

from faker import Faker

from app.config.integration import crud
from app.config.integration.models import User
from app.config.integration.schemas import UserCreate

fake = Faker(["pt_BR"])


def fake_password() -> str:
    return fake.password(length=32)


def fake_user_data(superUser: bool = False, active: bool = True) -> dict[str, Any]:
    data = {
        "email": fake.ascii_email(),
        "password": fake.password(length=32),
        "is_test": True,
        "is_active": active,
        "is_superuser": superUser,
    }
    data["username"] = data["email"]

    for item, value in data.items():
        setattr(fake_user_data, item, value)

    return data


async def create_fake_user(
    superUser: bool = False,
    active: bool = True,
    data: dict[str, Any] | None = None,
) -> User:
    if data:
        user_in = UserCreate(**data)
    else:
        user_in = UserCreate(**fake_user_data(superUser, active=active))

    user = await crud.user.create(obj_in=user_in)
    return user
