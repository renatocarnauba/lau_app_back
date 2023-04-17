import asyncio
import logging

from app.config.integration import crud
from app.config.settings import settings
from app.modules.lau_commons.models.user import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    asyncio.run(init_data())


async def init_data() -> None:
    user = await crud.user.get_by_email(email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await crud.user.create(obj_in=user_in)  # noqa: F841
    return None


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
