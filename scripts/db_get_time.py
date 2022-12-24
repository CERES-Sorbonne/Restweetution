import asyncio
import logging
import os
from time import time

import restweetution.config_loader as config

logging.basicConfig()
logging.root.setLevel(logging.INFO)

conf = config.load_system_config(os.getenv('SYSTEM_CONFIG'))


async def launch():
    storage = conf.build_storage()
    last = time()
    res = await storage.get_tweets()
    print(f'Retrieved {len(res)} tweets in {time() - last} seconds')

try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
