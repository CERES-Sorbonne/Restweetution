import asyncio
import datetime
import os
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
    token = await storage.get_token('david')

    client = AsyncClient(bearer_token=token, return_type=dict, wait_on_rate_limit=True)

    query = CollectionQuery()
    query.rule_ids = [71, 72, 15]

    async for data in storage.query_tweets_stream(query, chunk_size=100):
        tweet_ids = list(data.tweets.keys())
        raw_res = await client.get_tweets(tweet_ids, **ALL_CONFIG.twitter_format())
        tweets = [Tweet(**d) for d in raw_res['data']]
        existing_ids = {t.id for t in tweets}
        missing_ids = set(tweet_ids) - existing_ids

        await storage.save_tweets(tweets)

        timestamp = datetime.datetime.now()
        datas = [CustomData(id=t_id, key="missing", data={"deleted": True, "timestamp": timestamp}) for t_id in missing_ids]
        if datas:
            await storage.save_custom_datas(datas, override=False)


asyncio.run(main())
