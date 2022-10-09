import asyncio
import logging
import os
import restweetution.config_loader as config
from restweetution.data_view.elastic_dashboard import ElasticDashboard
from restweetution.data_view.status_view import StatusView
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    postgres_storage: PostgresStorage = main_conf.storages['local_postgres']
    elastic_storage: ElasticStorage = main_conf.storages['ceres_elastic']
    # view = ElasticDashboard(in_storage=postgres_storage, out_storage=elastic_storage, dashboard_name='david-dev')
    status_view = StatusView(main_conf.storage_manager, elastic_storage)
    status_view.update(2)
    # await view.load()
    # await view.save()

    streamer = main_conf.streamer
    await streamer.collect(main_conf.streamer_rules, main_conf.query_fields)

loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass