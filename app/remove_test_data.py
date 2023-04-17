import asyncio
import logging

from app.config.integration import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    asyncio.run(remove_test_data())


async def remove_test_data() -> None:
    await crud.user.remove_test()
    return None


def main() -> None:
    logger.info("Remove Test Data Started")
    init()
    logger.info("Remove Test Data Finished")


if __name__ == "__main__":
    main()
