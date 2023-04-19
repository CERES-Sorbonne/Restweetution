import asyncio
import datetime
import os
from time import time

import aiohttp
from tweepy.asynchronous import AsyncClient

from restweetution import config_loader
from restweetution.models.config.query_fields_preset import ALL_CONFIG
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.twitter import Tweet
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage

elastic: ElasticStorage


async def main():
    global elastic

    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))

    storage = conf.build_storage()
    users = await storage.get_restweet_users()
    user = [u for u in users if u.name == 'david'][0]

    client = AsyncClient(bearer_token=user.bearer_token, return_type=dict, wait_on_rate_limit=True)

    rule_ids = [71, 72, 15]

    async for tweet_chunk in storage.get_collected_tweets_stream(rule_ids=rule_ids, chunk_size=100):
        tweet_ids = {t.tweet_id for t in tweet_chunk}
        raw_res = await client.get_tweets(list(tweet_ids), **ALL_CONFIG.twitter_format())
        tweets = [Tweet(**d) for d in raw_res['data']]
        existing_ids = {t.id for t in tweets}
        missing_ids = tweet_ids - existing_ids

        await storage.save_tweets(tweets)

        timestamp = datetime.datetime.now()
        datas = [CustomData(id=t_id, key="missing", data={"deleted": True, "timestamp": timestamp}) for t_id in missing_ids]
        if datas:
            await storage.save_custom_datas(datas, override=False)

asyncio.run(main())
