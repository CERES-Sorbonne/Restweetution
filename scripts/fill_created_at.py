import asyncio
import datetime
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


async def main():
    global elastic

    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))

    storage = conf.build_storage()

    query = CollectionQuery()
    query.rule_ids = [47]

    total = 0

    async for data in storage.query_tweets_stream(query, chunk_size=100):
        tweets = data.get_linked_tweets()
        for tweet in tweets:
            matches = tweet.get_rule_matches()
            for match in matches:
                match.rule_id





asyncio.run(main())
