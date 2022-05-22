import asyncio
import logging
import os

import restweetution.config as config
from restweetution.collectors.async_streamer import AsyncStreamer
from restweetution.models.examples_config import ALL_CONFIG, MEDIUM_CONFIG, BASIC_CONFIG
from restweetution.storage import FileStorage
from restweetution.storage.elastic_storage.elastic_storage import ElasticStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

config = config.get_config()
config1 = {
    'token': config['token'],
    'tweets_storages': [
        ElasticStorage(config=config['elastic_config'], tags=['Rule'])
        # ElasticStorage(config={'url': 'http://localhost:9200', 'user': '', 'pwd': ''}, tags=['Rule'])
    ],
    'media_storages': [
        # no tags mean all media storages will be stored directly here
        FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'Media'), tags=['Bassem'])
    ],
    'verbose': True,
    'tweet_config': ALL_CONFIG.dict(),
    'average_hash': True
}


async def tprint():
    while True:
        await asyncio.sleep(1)
        print("not sleeeeeping")


async def launch():
    client = AsyncStreamer(config1)
    # await client.reset_rules()
    await client.add_rules({'Rule': '(johnny) OR (depp)'})
    # await client.add_rules({'XS': '(glace) OR (eau)'})
    # rules = await client.get_rules(['1527747516434874371'])
    # print(rules)
    # await client.remove_rules([1])
    # await client._api_get_rules()

    # asyncio.create_task(client._api_get_rules())
    # asyncio.create_task(tprint())
    task = asyncio.create_task(client.collect())
    # task = asyncio.create_task(run_server())
    await task


asyncio.run(launch())
