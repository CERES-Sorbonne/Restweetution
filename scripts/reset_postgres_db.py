import asyncio
import os

from pydantic import BaseModel

from restweetution import config_loader
from restweetution.models.config.user_config import UserConfig
from restweetution.storages.postgres_storage.models import Base

main_conf = config_loader.get_config_from_file(os.getenv('CONFIG'))


async def async_main():
    storage = main_conf.storage

    async with storage.get_engine().begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        await storage.save_user_configs([UserConfig(bearer_token=main_conf.bearer_token, name='local_conf')])

    await storage.get_engine().dispose()


asyncio.run(async_main())
