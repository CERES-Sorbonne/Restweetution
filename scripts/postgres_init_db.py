import asyncio
import os

from restweetution import config_loader

sys_conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))


async def async_main():
    storage = sys_conf.build_storage()
    await storage.build_tables()


asyncio.run(async_main())
