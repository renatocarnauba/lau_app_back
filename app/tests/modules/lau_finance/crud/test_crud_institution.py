import pytest

from app.config.integration import crud
from app.modules.lau_finance.models.institution import Institution, InstitutionCreate, InstitutionUpdate
from app.tests.modules.lau_finance.faker.fakeInstitution import (
    create_fake_institution,
    fake_institution_data,
)
from app.tests.utils.fakeUser import create_fake_user


@pytest.mark.asyncio
@pytest.mark.crud
async def test_create_institution() -> None:
    institution_in = InstitutionCreate(**fake_institution_data())
    user = await create_fake_user()
    institution = await crud.institution.create_with_owner(obj_in=institution_in, owner_id=str(user.id))
    assert institution.name == institution_in.name
    assert institution.owner_id == str(user.id)


@pytest.mark.asyncio
@pytest.mark.crud
async def test_get_institution() -> None:
    institution = await create_fake_institution()
    stored_institution = await crud.institution.get(id=institution.id)
    assert stored_institution
    assert institution.id == stored_institution.id
    assert institution.name == stored_institution.name
    assert institution.owner_id == stored_institution.owner_id


@pytest.mark.asyncio
@pytest.mark.crud
async def test_update_institution() -> None:
    institution = await create_fake_institution()
    institution_update = InstitutionUpdate(**fake_institution_data())
    institution2 = await crud.institution.update(db_obj=institution, obj_in=institution_update)
    assert institution.id == institution2.id
    assert institution.name != institution2.name
    assert institution2.name == institution_update.name
    assert institution.owner_id == institution2.owner_id


@pytest.mark.asyncio
@pytest.mark.crud
async def test_delete_institution() -> None:
    institution_in_manter = InstitutionCreate(**fake_institution_data())
    institution_in_excluir = InstitutionCreate(**fake_institution_data())
    user = await create_fake_user()
    institutionExcluir = await crud.institution.create_with_owner(obj_in=institution_in_excluir, owner_id=str(user.id))
    institutionManter = await crud.institution.create_with_owner(obj_in=institution_in_manter, owner_id=str(user.id))
    institutionExcluida = await crud.institution.remove(id=str(institutionExcluir.id))
    institutionExcluidaAposConsulta = await crud.institution.get(id=institutionExcluir.id)
    institutionMantidaAposConsulta = await crud.institution.get(id=institutionManter.id)
    assert institutionExcluidaAposConsulta is None
    assert institutionExcluida is not None
    institutionExcluidaX: Institution = institutionExcluida
    assert institutionExcluidaX.id == institutionExcluir.id
    assert institutionExcluidaX.name == institution_in_excluir.name
    assert institutionExcluidaX.owner_id == str(user.id)
    assert institutionMantidaAposConsulta is not None
    institutionMantidaAposConsultaX: Institution = institutionMantidaAposConsulta
    assert institutionMantidaAposConsultaX.id == institutionManter.id
    assert institutionMantidaAposConsultaX.name == institution_in_manter.name
    assert institutionMantidaAposConsultaX.owner_id == str(user.id)
