import asyncio
import logging
import os

import restweetution.config_loader as config

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():

    searcher = main_conf.searcher
    await searcher.collect(rule=main_conf.searcher_rule, fields=main_conf.query_fields, recent=True, start_time='2022-09-28T00:00:00Z')

try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
