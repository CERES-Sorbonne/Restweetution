import asyncio
import datetime
import logging
import os
from collections import defaultdict
from time import time

import aiohttp
from tweepy.asynchronous import AsyncClient

from restweetution import config_loader
from restweetution.models.config.query_fields_preset import ALL_CONFIG
from restweetution.models.linked.storage_collection import StorageCollection
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.queries import CollectionQuery
from restweetution.models.twitter import Tweet
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage

elastic: ElasticStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger('FillCreated')

async def main():
    global elastic

    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))

    storage = conf.build_storage()

    total = 0

    async for data in storage.get_rule_matches_stream(chunk_size=1000):
        tweet_ids = [d.tweet_id for d in data]
        bulk_data = await storage.query_tweets(query=CollectionQuery(tweet_ids=tweet_ids))
        await storage.save_bulk(bulk_data, override=True, ignore_tweets=True)
        total += len(bulk_data.get_tweets())
        logger.info(f'saved {len(bulk_data.get_tweets())}  total[{total}]')


asyncio.run(main())
