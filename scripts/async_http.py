import asyncio

import logging
import json
import os

from restweetution.collectors.async_streamer import AsyncStreamer
from restweetution.models.examples_config import MEDIUM_CONFIG
from restweetution.storage import FileStorage
from quart import Quart

app = Quart(__name__)


@app.route('/')
async def hello():
    return 'hello'


logging.basicConfig()
logging.root.setLevel(logging.INFO)

with open(os.getenv("CREDENTIALS"), "r") as f:
    token = json.load(f).get('token')

config1 = {
    'token': token,
    'tweets_storages': [
        FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'Data'), tags=['Rule']),
    ],
    'media_storages': [
        # no tags mean all media storages will be stored directly here
        FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'Media'), tags=['Bassem']),
    ],
    'verbose': True,
    'tweet_config': MEDIUM_CONFIG.dict(),
    'average_hash': True
}


async def tprint():
    while True:
        await asyncio.sleep(1)
        print("not sleeeeeping")


async def launch():
    asyncio.create_task(client.collect())
    asyncio.create_task(tprint())
    task = asyncio.create_task(app.run_task())
    await task


client = AsyncStreamer(config1)
# client.reset_rules()
client.set_rules({'Rule': '(johnny) OR (depp)'})
# asyncio.run(client.collect())
asyncio.run(launch())
