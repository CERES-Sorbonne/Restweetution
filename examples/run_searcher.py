import asyncio
import logging
import os

import restweetution.config_loader as config

logging.basicConfig()
logging.root.setLevel(logging.INFO)


async def launch():
    main_conf = config.get_config_from_file(os.getenv('CONFIG'))
    searcher = main_conf.searcher
    # view = ElasticDashboard(main_conf.storage_manager.main_storage, main_conf.storages['ceres_elastic'], 'renaud')
    await searcher.collect()


try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
