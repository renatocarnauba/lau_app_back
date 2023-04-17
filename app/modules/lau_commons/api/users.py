from typing import Any, List

from fastapi import APIRouter, Depends

from app.api import depsAsync
from app.config.integration import crud, models, schemas
from app.modules.lau_commons.core.exceptions import (
    UserAlreadyExists,
    UserNotFound,
    UserWithoutPrivileges,
)

router = APIRouter()


@router.get("/", response_model=List[models.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(depsAsync.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.UserView)
async def create_user(
    *,
    user_in: schemas.UserCreate,
    _: models.User = Depends(depsAsync.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(email=user_in.email)
    if user:
        raise UserAlreadyExists()
    user = await crud.user.create(obj_in=user_in)
    return user


@router.get("/me", response_model=models.User)
async def read_user_me(
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=models.User)
async def read_user_by_id(
    user_id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(id=user_id)
    if getattr(user, "id") == getattr(current_user, "id"):
        return user
    if not crud.user.is_superuser(current_user):
        raise UserWithoutPrivileges()
    return user


@router.put("/{user_id}", response_model=models.User)
async def update_user(
    *,
    user_id: str,
    user_in: schemas.UserUpdate,
    _: models.User = Depends(depsAsync.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(id=user_id)
    if not user:
        raise UserNotFound()
    user = await crud.user.update(db_obj=user, obj_in=user_in)
    return user
