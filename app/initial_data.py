import asyncio
import logging

from app import schemas
from app.config.integration import crud
from app.config.settings import settings
from app.db.sessionAsync import sessionLocal as sessionLocalAsync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    asyncio.run(init_data())


async def init_data() -> None:
    user = await crud.user.get_by_email(sessionLocalAsync, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await crud.user.create(sessionLocalAsync, obj_in=user_in)  # noqa: F841
    return None


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
