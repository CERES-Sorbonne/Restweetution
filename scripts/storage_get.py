import asyncio
import logging
import os

import restweetution.config as config
from restweetution.storage.storage_manager.storage_join import FirstFoundJoin

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    storage = main_conf.storage_manager
    res = await storage.get_medias()
    print(len(res))
    print(len([r.sha1 for r in res if r.sha1]))


loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
