import asyncio
import logging
import os
from time import time

import restweetution.config_loader as config

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    last = time()
    res = await main_conf.storage.get_tweet_ids()
    print(res)
    print(time() - last)


try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
