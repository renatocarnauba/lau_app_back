# from typing import Dict

# import pytest
# from httpx import AsyncClient

# from app.modules.lau_commons.core.config import settings
# from app.main import app


# @pytest.mark.anyio
# @pytest.mark.api
# async def test_celery_worker_test(superuser_token_headers: Dict[str, str]) -> None:
#     data = {"msg": "test"}
#     async with AsyncClient(
#         app=app, base_url=f"{str(settings.SERVER_HOST).removesuffix('/')}:{settings.SERVER_PORT}/"
#     ) as ac:
#         r = await ac.post(
#             f"{settings.API_V1_STR}/utils/test-celery/",
#             json=data,
#             headers=superuser_token_headers,
#         )
#         response = r.json()
#         assert response["msg"] == "Word received"
