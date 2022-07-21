import asyncio
import json
import logging
import os

import restweetution.config as config

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    storage = main_conf.storage_tweet_storages[0]
    res = await storage.get_medias()
    print(res[0])



loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
