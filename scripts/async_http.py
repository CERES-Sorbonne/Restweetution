import asyncio
import logging

import restweetution.config as config
from restweetution.collectors.async_streamer import AsyncStreamer
from restweetution.models.examples_config import ALL_CONFIG
from restweetution.storage.async_storage_manager import AsyncStorageManager
from restweetution.storage.elastic_storage.elastic_storage import ElasticTweetStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

config = config.get_config()

es_storage = ElasticTweetStorage(es_config=config['elastic_config'])
# es_storage = ElasticTweetStorage(name='Localhost_Elastic',
#                                  es_config={
#                                      "url": "http://localhost:9200",
#                                      "user": "",
#                                      "pwd": ""}
#                                  )
config1 = {
    'token': config['token'],
    'verbose': False,
    'tweet_config': ALL_CONFIG.dict(),
    'average_hash': True
}

async def launch():

    storage_manager = AsyncStorageManager()
    storage_manager.add_storage(es_storage, ['Rule'])
    streamer = AsyncStreamer(storage_manager, config1)
    await streamer.add_stream_rules({'Rule': '(johnny) OR (depp)'})

    asyncio.create_task(streamer.collect())
    # asyncio.create_task(run_server())
    # await task

loop = asyncio.get_event_loop()
loop.create_task(launch())
loop.run_forever()
