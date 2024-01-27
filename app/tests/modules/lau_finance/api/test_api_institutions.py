from typing import Any

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules import lau_finance
from app.modules.lau_commons.core.exceptions import (
    InstitutionNotFound,
    UserWithoutPrivileges,
)
from app.tests.modules.lau_finance.faker.fakeInstitution import (
    create_fake_institution,
    create_fake_institution_mine,
    fake_institution_data,
)
from app.tests.utils.fakeUser import fake_user_data
from app.tests.utils.utils import (
    check_error_class,
    check_list_in_list,
    compare_two_lists,
    fake_company,
)


class ValueStorage:
    tbInstitutions: list[dict[str, Any]] = []


@pytest.mark.anyio
@pytest.mark.api
async def test_retrieve_institution_mine(normaluser_token_headers: dict[str, Any]) -> None:
    tbInstitutions = []
    for _ in range(5):
        act = await create_fake_institution_mine(normaluser_token_headers)
        acctDict = dict(act.__dict__)
        acctDict = jsonable_encoder(acctDict)
        tbInstitutions.append(acctDict)

    ValueStorage.tbInstitutions = tbInstitutions
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/mine", headers=normaluser_token_headers
        )
        assert r.status_code == 200
        tbInstitutionsReceived = r.json()

        assert compare_two_lists(tbInstitutions, tbInstitutionsReceived)


@pytest.mark.anyio
@pytest.mark.api
async def test_retrieve_institution_normaluser(normaluser_token_headers: dict[str, Any]) -> None:
    tbInstitutions = ValueStorage.tbInstitutions

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/", headers=normaluser_token_headers)
        assert r.status_code == 200
        tbInstitutionsReceived = r.json()
        assert compare_two_lists(tbInstitutions, tbInstitutionsReceived)


@pytest.mark.anyio
@pytest.mark.api
async def test_retrieve_institution_superuser(superuser_token_headers: dict[str, Any]) -> None:
    tbInstitutions = []
    for _ in range(5):
        act = await create_fake_institution_mine(superuser_token_headers)
        acctDict = dict(act.__dict__)
        acctDict = jsonable_encoder(acctDict)
        tbInstitutions.append(acctDict)

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/", headers=superuser_token_headers)
        assert r.status_code == 200
        tbInstitutionsReceived = r.json()
        assert check_list_in_list(tbInstitutions + ValueStorage.tbInstitutions, tbInstitutionsReceived)


@pytest.mark.anyio
@pytest.mark.api
async def test_create_institution(normaluser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.post(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/",
            headers=normaluser_token_headers,
            json=fake_institution_data(),
        )
        created_user = r.json()
        assert r.status_code == 200
        assert "_id" not in created_user
        assert "id" in created_user


@pytest.mark.anyio
@pytest.mark.api
async def test_update_institution(superuser_token_headers: dict[str, Any]) -> None:
    data = fake_institution_data()
    institution = await create_fake_institution(data=data)

    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/{institution.id}",
            headers=superuser_token_headers,
            json=data,
        )
    assert 200 <= r.status_code < 300
    stored_institution = await crud.institution.get(id=institution.id)
    assert stored_institution
    assert stored_institution.name == name


@pytest.mark.anyio
@pytest.mark.api
async def test_update_institution_user_without_privilegies(normaluser_token_headers: dict[str, Any]) -> None:
    data = fake_institution_data()
    institution = await create_fake_institution(data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/{institution.id}",
            headers=normaluser_token_headers,
            json=data,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
@pytest.mark.api
async def test_update_institution_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.put(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/0",
            headers=superuser_token_headers,
            json=fake_user_data(),
        )
        check_error_class(errorClass=InstitutionNotFound, response=r)


@pytest.mark.anyio
@pytest.mark.api
async def test_delete_institution(superuser_token_headers: dict[str, Any]) -> None:
    data = fake_institution_data()
    institution = await create_fake_institution(data=data)

    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/{institution.id}",
            headers=superuser_token_headers,
        )
    assert 200 <= r.status_code < 300
    stored_institution = await crud.institution.get(id=institution.id)
    assert not stored_institution


@pytest.mark.anyio
@pytest.mark.api
async def test_delete_institution_user_without_privilegies(normaluser_token_headers: dict[str, Any]) -> None:
    data = fake_institution_data()
    institution = await create_fake_institution(data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/{institution.id}",
            headers=normaluser_token_headers,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
@pytest.mark.api
async def test_delete_institution_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.delete(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/0",
            headers=superuser_token_headers,
        )
        check_error_class(errorClass=InstitutionNotFound, response=r)


@pytest.mark.anyio
@pytest.mark.api
async def test_get_institution(superuser_token_headers: dict[str, Any]) -> None:
    data = fake_institution_data()
    institution = await create_fake_institution(data=data)

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/{institution.id}",
            headers=superuser_token_headers,
        )
    assert 200 <= r.status_code < 300
    stored_institution = await crud.institution.get(id=institution.id)
    assert stored_institution
    assert stored_institution.name == data["name"]
    assert stored_institution.id == institution.id


@pytest.mark.anyio
@pytest.mark.api
async def test_get_institution_user_without_privilegies(normaluser_token_headers: dict[str, Any]) -> None:
    data = fake_institution_data()
    institution = await create_fake_institution(data=data)
    name = fake_company()
    data["name"] = name

    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/{institution.id}",
            headers=normaluser_token_headers,
        )
        check_error_class(errorClass=UserWithoutPrivileges, response=r)


@pytest.mark.anyio
@pytest.mark.api
async def test_get_institution_notFound(superuser_token_headers: dict[str, Any]) -> None:
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.get(
            f"{settings.API_V1_STR}/{lau_finance.__module__}/institutions/0",
            headers=superuser_token_headers,
        )
        check_error_class(errorClass=InstitutionNotFound, response=r)
