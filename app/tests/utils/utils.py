from typing import Any, Dict

import pytest
from faker import Faker
from httpx import AsyncClient, Response

from app.config.integration import crud
from app.config.settings import settings
from app.main import app
from app.modules.lau_commons.core.exceptions import ErrorBase
from app.modules.lau_commons.models.user import UserCreate
from app.tests.utils.fakeUser import fake_user_data

fake = Faker(["pt_BR"])


def fake_company() -> str:
    return fake.company()


def compare_two_lists(list1: list[dict[str, Any]], list2: list[dict[str, Any]]) -> bool:
    """
    Compare two lists and logs the difference.
    :param list1: first list.
    :param list2: second list.
    :return:      if there is difference between both lists.
    """
    diff = [i for i in list1 + list2 if i not in list1 or i not in list2]
    result = len(diff) == 0
    return result


def check_list_in_list(list1: list[dict[str, Any]], list2: list[dict[str, Any]]) -> bool:
    """
    Compare two lists and logs the difference.
    :param list1: first list.
    :param list2: second list.
    :return:      if there is difference between both lists.
    """
    diff = [i for i in list1 if i not in list2]
    result = len(diff) == 0
    return result


def genHeader(r: Response) -> Dict[str, str]:
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.mark.anyio
async def get_superuser_token_headers() -> Dict[str, str]:
    user_in = UserCreate(**fake_user_data(superUser=True))
    await crud.user.create(obj_in=user_in)
    login_data = {
        "username": user_in.email,
        "password": user_in.password,
    }
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        return genHeader(r)


@pytest.mark.anyio
async def get_normaluser_token_headers() -> Dict[str, str]:
    user_in = UserCreate(**fake_user_data())
    await crud.user.create(obj_in=user_in)
    login_data = {
        "username": user_in.email,
        "password": user_in.password,
    }
    async with AsyncClient(
        app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
    ) as ac:
        r = await ac.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        return genHeader(r)


def check_error_class(errorClass: ErrorBase, response: Response) -> None:
    assert response.status_code == errorClass().status_code
    tokens = response.json()
    assert "detail" in tokens
    assert tokens["detail"] == errorClass().detail
