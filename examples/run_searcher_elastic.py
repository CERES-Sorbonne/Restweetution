import asyncio
import logging
import os
from datetime import datetime

import restweetution.config_loader as config
from restweetution.data_view.elastic_dashboard import ElasticDashboard

logging.basicConfig()
logging.root.setLevel(logging.INFO)


async def launch():
    main_conf = config.get_config_from_file(os.getenv('CONFIG'))
    searcher = main_conf.searcher
    view = ElasticDashboard(main_conf.storage.main_storage, main_conf.storages['ceres_elastic'], 'renaud')
    # await view.load()
    # await view.save()

    await searcher.collect()


try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
