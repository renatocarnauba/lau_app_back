from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app import schemas
from app.api import depsAsync
from app.config.integration import crud, models
from app.core.exceptions import UserAlreadyExists, UserNotFound, UserWithoutPrivileges

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
async def read_users(
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(depsAsync.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(asyncSection, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    user_in: schemas.UserCreate,
    _: models.User = Depends(depsAsync.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(asyncSection, email=user_in.email)
    if user:
        raise UserAlreadyExists()
    user = await crud.user.create(asyncSection, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    _: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(asyncSection, id=user_id)
    if getattr(user, "id") == getattr(current_user, "id"):
        return user
    if not crud.user.is_superuser(current_user):
        raise UserWithoutPrivileges()
    return user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    user_id: int,
    user_in: schemas.UserUpdate,
    _: models.User = Depends(depsAsync.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(asyncSection, id=user_id)
    if not user:
        raise UserNotFound()
    user = await crud.user.update(asyncSection, db_obj=user, obj_in=user_in)
    return user
