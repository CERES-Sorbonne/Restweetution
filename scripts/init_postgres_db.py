import asyncio
import os

from restweetution import config_loader
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage

sys_conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))


async def async_main():
    storage = PostgresJSONBStorage(sys_conf.postgres_url)

    await storage.build_tables()


asyncio.run(async_main())
