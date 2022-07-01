import asyncio

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from restweetution.storage.postgres_storage.models import Base, Rule

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
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # async with async_session() as session:

        # await session.commit()

    await engine.dispose()

asyncio.run(async_main())
