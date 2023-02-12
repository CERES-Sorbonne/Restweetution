import asyncio
import os

from restweetution import config_loader


async def main():
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
    storage = conf.build_storage()

    async for res in storage.get_collected_tweets_stream(
            rule_ids=[348, 333, 341, 340, 334, 338, 345, 337, 339, 335, 336, 342, 331, 343, 334, 332],
            direct_hit=True):
        print(len(res))


asyncio.run(main())
