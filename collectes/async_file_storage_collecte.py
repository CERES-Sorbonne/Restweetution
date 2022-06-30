import asyncio
import json
import logging
import os

from restweetution.collectors import AsyncStreamer
from restweetution.collectors.async_client import AsyncClient
from restweetution.models.config.query_params_config import MEDIUM_CONFIG
from restweetution.storage.async_storage_manager import AsyncStorageManager
from restweetution.storage.object_storage.async_object_storage import AsyncFileStorage
from restweetution.utils import set_error_handler


def my_error_handler(e: Exception):
    print("THIS IS MY ERROR, NOT THE DEFAULT ONE")


async def launch():
    with open(os.getenv("CREDENTIALS"), "r") as f:
        token = json.load(f).get('token')

    stm = AsyncStorageManager()
    client = AsyncClient(token=token)
    stm.add_storage(AsyncFileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'Data')), tags=['ZM', 'IVG'])
    s = AsyncStreamer(client, stm)
    s.set_query_params(MEDIUM_CONFIG)
    set_error_handler(my_error_handler)
    s.create_error()
    asyncio.create_task(s.collect())

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(launch())
    loop.run_forever()