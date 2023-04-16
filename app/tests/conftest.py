import asyncio
from asyncio.unix_events import DefaultEventLoopPolicy
from typing import Any, Dict, Iterator

import pytest
from odmantic import AIOEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.db.sessionAsync import sessionLocal as sessionLocalAsync
from app.db.sessionAsyncMongo import sessionLocal as sessionLocalAsyncMongo
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


@pytest.fixture(scope="session")
def asyncSection() -> Iterator[async_sessionmaker[AsyncSession]]:
    yield sessionLocalAsync


@pytest.fixture(scope="session")
def asyncSectionMongo() -> Iterator[AIOEngine]:
    yield sessionLocalAsyncMongo


@pytest.fixture(scope="module")
async def superuser_token_headers() -> Dict[str, str]:
    return await get_superuser_token_headers()


@pytest.fixture(scope="module")
async def normaluser_token_headers() -> Dict[str, str]:
    return await get_normaluser_token_headers()
