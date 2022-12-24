import asyncio
import os

from restweetution import config_loader


async def main():
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
    postgres = conf.build_storage()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
