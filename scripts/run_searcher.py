import asyncio
import logging
import os

from tweepy.asynchronous import AsyncClient

import restweetution.config as config
from restweetution.collectors.searcher import Searcher
from restweetution.models.config.stream_query_params import ALL_CONFIG

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():

    searcher = Searcher(bearer_token=main_conf.client_token, storage=main_conf.storage_manager)
    res = await searcher.get_users(ids=['759364749897314304', '77638302401976729'])
    print(res)

try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
