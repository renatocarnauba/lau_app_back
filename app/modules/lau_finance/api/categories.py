from typing import Any, List

from fastapi import APIRouter, Depends

from app.api import depsAsync
from app.config.integration import crud, models
from app.modules.lau_commons.core.exceptions import (
    CategoryNotFound,
    UserWithoutPrivileges,
)
from app.modules.lau_finance.models.category import (
    CategoryCreate,
    CategoryOrm,
    CategoryUpdate,
    CategoryView,
)

router = APIRouter()


@router.get("/mine", response_model=List[CategoryView])
async def read_categories_mine(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve categories Mine.
    """
    categories = await crud.category.get_multi_by_owner(owner_id=str(current_user.id), skip=skip, limit=limit)
    return categories


@router.get("/", response_model=List[CategoryView])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve categories.
    """
    if crud.user.is_superuser(current_user):
        categories = await crud.category.get_multi(skip=skip, limit=limit)
    else:
        categories = await crud.category.get_multi_by_owner(owner_id=str(current_user.id), skip=skip, limit=limit)
    return categories


@router.post("/", response_model=CategoryView)
async def create_category(
    *,
    category_in: CategoryCreate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Create new category.
    """
    category: CategoryOrm = await crud.category.create_with_owner(obj_in=category_in, owner_id=str(current_user.id))
    return category


@router.put("/{id}", response_model=CategoryView)
async def update_category(
    *,
    id: str,
    category_in: CategoryUpdate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Update an category.
    """
    category = await crud.category.get(id=id)
    if not category:
        raise CategoryNotFound()
    if not crud.user.is_superuser(current_user) and (category.owner_id != current_user.id):
        raise UserWithoutPrivileges()

    category = await crud.category.update(db_obj=category, obj_in=category_in)
    return category


@router.get("/{id}", response_model=CategoryView)
async def read_category(
    *,
    id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get category by ID.
    """
    category = await crud.category.get(id=id)
    if not category:
        raise CategoryNotFound()
    if not crud.user.is_superuser(current_user) and (category.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    return category


@router.delete("/{id}", response_model=CategoryView)
async def delete_category(
    *,
    id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Delete an category.
    """
    category = await crud.category.get(id=id)
    if not category:
        raise CategoryNotFound()
    if not crud.user.is_superuser(current_user) and (category.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    category = await crud.category.remove(id=id)
    return category
