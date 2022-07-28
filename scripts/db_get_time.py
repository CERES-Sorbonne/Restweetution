import asyncio
import datetime
import logging
import os
import restweetution.config as config
from restweetution.data_view.data_view import ElasticView
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    postgres_storage: PostgresStorage = main_conf.storages['local_postgres']
    elastic_storage: ElasticStorage = main_conf.storages['ceres_elastic']

    view = ElasticView(in_storage=postgres_storage, out_storage=elastic_storage)
    last = datetime.datetime.now().second
    # print(last)
    await view.load()
    print(datetime.datetime.now().second - last)
    # await view.save()

loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
