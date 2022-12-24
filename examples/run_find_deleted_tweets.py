import asyncio
import logging
import os

import restweetution.config_loader as config
from restweetution.models.config.query_fields import QueryFields

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():

    searcher = main_conf.searcher
    storage = main_conf.storages['local_postgres']

    tweets = await storage.get_tweets()
    ids = [t.id for t in tweets]

    res = await searcher.get_tweets(ids=ids)
    print(f'{len(res.missing)} tweets have been removed')
    for id_ in res.missing:
        print(id_)

try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
