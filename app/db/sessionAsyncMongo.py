from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from app.config.settings import settings


def get_engine():
    client = AsyncIOMotorClient(str(settings.MONGODB_URL))
    engine = AIOEngine(client=client, database=str(settings.MONGODB_DEFAULT_DB))
    return engine


sessionLocal = get_engine()
