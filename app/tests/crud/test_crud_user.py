import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.config.integration import crud
from app.core.security import verify_password
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.fakeUser import create_fake_user, fake_password, fake_user_data


@pytest.mark.asyncio
async def test_create_user(asyncSection: async_sessionmaker[AsyncSession]) -> None:
    user_in = UserCreate(**fake_user_data())
    user = await crud.user.create(asyncSection, obj_in=user_in)
    assert user.email == user_in.email
    assert hasattr(user, "hashed_password")


@pytest.mark.asyncio
async def test_authenticate_user(asyncSection: async_sessionmaker[AsyncSession]) -> None:
    user_in = UserCreate(**fake_user_data())
    user = await crud.user.create(asyncSection, obj_in=user_in)
    authenticated_user = await crud.user.authenticate(
        asyncSection=asyncSection, email=user_in.email, password=user_in.password
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


@pytest.mark.asyncio
async def test_not_authenticate_user(asyncSection: async_sessionmaker[AsyncSession]) -> None:
    user_in = UserCreate(**fake_user_data())
    authenticated_user = await crud.user.authenticate(
        asyncSection=asyncSection, email=user_in.email, password=user_in.password
    )
    assert authenticated_user is None


@pytest.mark.asyncio
async def test_check_if_user_is_active(asyncSection: async_sessionmaker[AsyncSession]) -> None:
    user_in = UserCreate(**fake_user_data())
    user = await crud.user.create(asyncSection=asyncSection, obj_in=user_in)
    assert crud.user.is_active(user) is True


@pytest.mark.asyncio
async def test_check_if_user_is_active_inactive(asyncSection: async_sessionmaker[AsyncSession]) -> None:
    user_in = UserCreate(**fake_user_data(active=False))
    user = await crud.user.create(asyncSection=asyncSection, obj_in=user_in)
    assert crud.user.is_active(user) is False


@pytest.mark.asyncio
async def test_check_if_user_is_superuser(asyncSection: async_sessionmaker[AsyncSession]) -> None:
    user_in = UserCreate(**fake_user_data(superUser=True))
    user = await crud.user.create(asyncSection=asyncSection, obj_in=user_in)
    assert crud.user.is_superuser(user) is True


@pytest.mark.asyncio
async def test_check_if_user_is_superuser_normal_user(
    asyncSection: async_sessionmaker[AsyncSession],
) -> None:
    user_in = UserCreate(**fake_user_data(superUser=False))
    user = await crud.user.create(asyncSection=asyncSection, obj_in=user_in)
    assert crud.user.is_superuser(user) is False


@pytest.mark.asyncio
async def test_get_user(asyncSection: async_sessionmaker[AsyncSession]) -> None:
    user = await create_fake_user(asyncSection=asyncSection, superUser=True)
    user_queried = await crud.user.get(asyncSection=asyncSection, id=user.id)
    assert user_queried
    assert user.email == user_queried.email
    assert jsonable_encoder(user) == jsonable_encoder(user_queried)


@pytest.mark.asyncio
async def test_update_user(asyncSection: async_sessionmaker[AsyncSession]) -> None:
    user = await create_fake_user(asyncSection=asyncSection, superUser=True)
    new_password = fake_password()
    user_in_update = UserUpdate(password=new_password)
    await crud.user.update(asyncSection=asyncSection, db_obj=user, obj_in=user_in_update)
    user_queried = await crud.user.get(asyncSection=asyncSection, id=user.id)
    assert user_queried
    assert user.email == user_queried.email
    assert verify_password(new_password, str(user_queried.hashed_password))