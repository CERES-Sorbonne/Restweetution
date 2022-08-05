import asyncio
import logging
import os

import restweetution.config as config
from restweetution.collectors.searcher import Searcher
from restweetution.models.rule import SearcherRule

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():

    searcher = Searcher(bearer_token=main_conf.bearer_token, storage=main_conf.storage_manager)
    await searcher.collect(SearcherRule(tag='Hiking', query='#hiking'), fields=main_conf.query_fields)

try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
