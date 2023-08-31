from typing import Any, List

from fastapi import APIRouter, Depends

from app.api import depsAsync
from app.config.integration import crud, models
from app.modules.lau_commons.core.exceptions import (
    InstitutionNotFound,
    UserWithoutPrivileges,
)
from app.modules.lau_finance.models.institution import (
    Institution,
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionView,
)

router = APIRouter()


@router.get("/mine", response_model=List[InstitutionView])
async def read_institutions_mine(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve institutions Mine.
    """
    institutions = await crud.institution.get_multi_by_owner(owner_id=str(current_user.id), skip=skip, limit=limit)
    return institutions


@router.get("/", response_model=List[InstitutionView])
async def read_institutions(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Retrieve institutions.
    """
    if crud.user.is_superuser(current_user):
        institutions = await crud.institution.get_multi(skip=skip, limit=limit)
    else:
        institutions = await crud.institution.get_multi_by_owner(owner_id=str(current_user.id), skip=skip, limit=limit)
    return institutions


@router.post("/", response_model=InstitutionView)
async def create_institution(
    *,
    institution_in: InstitutionCreate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Create new institution.
    """
    institution: Institution = await crud.institution.create_with_owner(
        obj_in=institution_in, owner_id=str(current_user.id)
    )
    return institution


@router.put("/{id}", response_model=InstitutionView)
async def update_institution(
    *,
    id: str,
    institution_in: InstitutionUpdate,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Update an institution.
    """
    institution = await crud.institution.get(id=id)
    if not institution:
        raise InstitutionNotFound()
    if not crud.user.is_superuser(current_user) and (institution.owner_id != current_user.id):
        raise UserWithoutPrivileges()

    institution = await crud.institution.update(db_obj=institution, obj_in=institution_in)
    return institution


@router.get("/{id}", response_model=InstitutionView)
async def read_institution(
    *,
    id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Get institution by ID.
    """
    institution = await crud.institution.get(id=id)
    if not institution:
        raise InstitutionNotFound()
    if not crud.user.is_superuser(current_user) and (institution.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    return institution


@router.delete("/{id}", response_model=InstitutionView)
async def delete_institution(
    *,
    id: str,
    current_user: models.User = Depends(depsAsync.get_current_active_user),
) -> Any:
    """
    Delete an institution.
    """
    institution = await crud.institution.get(id=id)
    if not institution:
        raise InstitutionNotFound()
    if not crud.user.is_superuser(current_user) and (institution.owner_id != current_user.id):
        raise UserWithoutPrivileges()
    institution = await crud.institution.remove(id=id)
    return institution
