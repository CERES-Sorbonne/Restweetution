import asyncio
import os

from restweetution import config_loader
from restweetution.storages.postgres_storage.models import Base

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def async_main():
    storage = main_conf.storages['local_postgres']

    async with storage.get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await storage.get_engine().dispose()


asyncio.run(async_main())
