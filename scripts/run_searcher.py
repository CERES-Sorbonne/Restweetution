import asyncio
import logging
import os

from tweepy.asynchronous import AsyncClient

import restweetution.config as config
from restweetution.collectors.searcher import Searcher
from restweetution.models.config.stream_query_params import ALL_CONFIG
from restweetution.models.twitter import SearcherRule

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():

    searcher = Searcher(bearer_token=main_conf.client_token, storage=main_conf.storage_manager)
    await searcher.collect(SearcherRule(tag='Hiking', query='#hiking'))

try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
