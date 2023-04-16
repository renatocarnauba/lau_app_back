from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config.settings import settings

engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI_ASYNC), pool_pre_ping=True)
sessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
