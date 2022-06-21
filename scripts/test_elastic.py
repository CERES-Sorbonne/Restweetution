import asyncio
import logging
import os

import restweetution.config as config
from restweetution.models.examples_config import ALL_CONFIG

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    streamer = main_conf.streamer
    streamer.set_query_params(ALL_CONFIG)

    await streamer.collect()


loop = asyncio.get_event_loop()
loop.create_task(launch())
loop.run_forever()
