import asyncio
import json
import logging
import os

from restweetution.collectors import AsyncStreamer
from restweetution.models.config.query_params_config import MEDIUM_CONFIG
from restweetution.storage.async_storage_manager import AsyncStorageManager
from restweetution.storage.object_storage.async_object_storage import AsyncFileStorage


async def launch():
    with open(os.getenv("CREDENTIALS"), "r") as f:
        token = json.load(f).get('token')
    config = {
        'token': token,
        'verbose': True,
        'tweet_config': MEDIUM_CONFIG.dict(),
        'average_hash': True
    }
    stm = AsyncStorageManager(download_media=True)
    stm.add_storage(AsyncFileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'Data'), tags=['ZM']))
    s = AsyncStreamer(stm, config)
    asyncio.create_task(s.collect())

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(launch())
    loop.run_forever()