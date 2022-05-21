import asyncio

import logging
import json
import os

from restweetution.collectors.async_streamer import AsyncStreamer
from restweetution.models.examples_config import MEDIUM_CONFIG, ALL_CONFIG
from restweetution.storage import FileStorage

from restweetution.storage.elastic_storage.elastic_storage import ElasticStorage

from restweetution.server.config_server import run_server

logging.basicConfig()
logging.root.setLevel(logging.INFO)

with open(os.getenv("CREDENTIALS"), "r") as f:
    token = json.load(f).get('token')

config1 = {
    'token': token,
    'tweets_storages': [
        ElasticStorage(tags=['Rule']),
    ],
    'media_storages': [
        # no tags mean all media storages will be stored directly here
        FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'Media'), tags=['Bassem']),
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
