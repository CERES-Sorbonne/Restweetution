import asyncio
import logging
import restweetution.config_loader as config
from fastapi import FastAPI

from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file('/Users/david/Restweetution/private_config/config.yaml')


async def launch():
    streamer = main_conf.streamer
    # print(main_conf.streamer_rules)
    conf = main_conf.storages['ceres_elastic'].get_config()
    print(conf)
    storage = ElasticStorage(**conf)
    # await storage.save_custom_datas([CustomData(key='test', id='1', data=conf)])
    # await streamer.collect(rules=main_conf.streamer_rules, fields=main_conf.query_fields)

loop = asyncio.get_event_loop()
loop.create_task(launch())

# app = FastAPI()
#
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
