import asyncio
import logging
import os
from datetime import datetime

import restweetution.config as config
from restweetution.data_view.elastic_dashboard import ElasticDashboard
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    postgres_storage: PostgresStorage = main_conf.storages['local_postgres']
    elastic_storage: ElasticStorage = main_conf.storages['ceres_elastic']

    view = ElasticDashboard(in_storage=postgres_storage, out_storage=elastic_storage)
    last = datetime.now().second
    # print(last)
    await view.load()
    print(datetime.now().second - last)
    await view.save()


try:
    asyncio.run(launch())
except KeyboardInterrupt as e:
    pass
