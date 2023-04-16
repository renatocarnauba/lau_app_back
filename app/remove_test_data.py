import asyncio
import logging

from app.config.integration import crud
from app.db.sessionAsync import sessionLocal as sessionLocalAsync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    asyncio.run(remove_test_data())


async def remove_test_data() -> None:
    await crud.user.remove_test(sessionLocalAsync)
    return None


def main() -> None:
    logger.info("Remove Test Data Started")
    init()
    logger.info("Remove Test Data Finished")


if __name__ == "__main__":
    main()
