import asyncio
import logging
import os

import restweetution.config as config
from collectes.dump2 import tweet1, tweet2

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))

async def listener(data):
    print(data)

async def launch():
    streamer = main_conf.streamer
    # main_conf.storage_tweet_storages[0].listen_save_event(listener)
    await streamer.collect()

loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
