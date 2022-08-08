import asyncio
import logging
import os

import restweetution.config as config

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():

    searcher = main_conf.searcher
    await searcher.collect(main_conf.searcher_rule, fields=main_conf.query_fields)

try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
