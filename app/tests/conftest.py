import asyncio
from asyncio.unix_events import DefaultEventLoopPolicy
from typing import Any, Dict

import pytest

from app.tests.utils.utils import (
    get_normaluser_token_headers,
    get_superuser_token_headers,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop() -> Any | DefaultEventLoopPolicy | None:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def superuser_token_headers() -> Dict[str, str]:
    return await get_superuser_token_headers()


@pytest.fixture(scope="module")
async def normaluser_token_headers() -> Dict[str, str]:
    return await get_normaluser_token_headers()
