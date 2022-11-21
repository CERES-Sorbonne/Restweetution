import asyncio
import logging
import os

import restweetution.config_loader as config
from restweetution.data_view.elastic_dashboard import ElasticDashboard
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    elastic_storage: ElasticStorage = main_conf.exporters['ceres_elastic']
    view = ElasticDashboard(in_storage=main_conf.storage, out_storage=elastic_storage, dashboard_name='david-dev')
    # status_view = StatusView(main_conf.storage, elastic_storage)

    streamer = main_conf.streamer
    await streamer.collect(main_conf.streamer_rules, main_conf.query_fields)

loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
