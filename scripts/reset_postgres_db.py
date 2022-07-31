import asyncio

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from restweetution.storages.postgres_storage.models import Base

db_string = "postgresql+asyncpg://localhost/david"

db = create_engine(db_string)

engine = create_async_engine(
    db_string,
    echo=False,
)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def async_main():
    global engine, async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


asyncio.run(async_main())
