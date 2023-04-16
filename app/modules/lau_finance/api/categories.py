from typing import Any, List

from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.api import depsAsyncMongo, depsAsync
from app.config.integration import crud, models
from app.core.exceptions import CategoryNotFound, UserWithoutPrivileges
from app.modules.lau_finance.models.nosql.category import (
    CategoryCreate,
    CategoryOrm,
    CategoryUpdate,
    CategoryView,
)

router = APIRouter()


@router.get("/mine", response_model=List[CategoryView])
async def read_categories_mine(
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve categories Mine.
    """
    categories = await crud.category.get_multi_by_owner(
        asyncSection=asyncSection, owner_id=int(current_user.id), skip=skip, limit=limit
    )
    return categories


@router.get("/", response_model=List[CategoryView])
async def read_categories(
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve categories.
    """
    if crud.user.is_superuser(current_user):
        categories = await crud.category.get_multi(asyncSection=asyncSection, skip=skip, limit=limit)
    else:
        categories = await crud.category.get_multi_by_owner(
            asyncSection=asyncSection, owner_id=int(current_user.id), skip=skip, limit=limit
        )
    return categories


@router.post("/", response_model=CategoryView)
async def create_category(
    *,
    asyncSectionMongo: AIOEngine = Depends(depsAsyncMongo.get_asyncSection),
    category_in: CategoryCreate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Create new category.
    """
    category: CategoryOrm = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in, owner_id=int(current_user.id)
    )
    return category


@router.put("/{id}", response_model=CategoryView)
async def update_category(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    id: int,
    category_in: CategoryUpdate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Update an category.
    """
    category = await crud.category.get(asyncSection=asyncSection, id=id)
    if not category:
        raise CategoryNotFound()
    if not crud.user.is_superuser(current_user) and (category.owner_id != current_user.id):
        raise UserWithoutPrivileges()

    category = await crud.category.update(asyncSection=asyncSection, db_obj=category, obj_in=category_in)
    return category


@router.get("/{id}", response_model=CategoryView)
async def read_category(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    id: int,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get category by ID.
    """
    category = await crud.category.get(asyncSection=asyncSection, id=id)
    if not category:
        raise CategoryNotFound()
    if not crud.user.is_superuser(current_user) and (category.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    return category


@router.delete("/{id}", response_model=CategoryView)
async def delete_category(
    *,
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    id: int,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Delete an category.
    """
    category = await crud.category.get(asyncSection=asyncSection, id=id)
    if not category:
        raise CategoryNotFound()
    if not crud.user.is_superuser(current_user) and (category.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    category = await crud.category.remove(asyncSection=asyncSection, id=id)
    return category
