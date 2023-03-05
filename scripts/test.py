import asyncio
import os
import time
from collections import defaultdict
from typing import List

import aiohttp
import tweepy
from aiopath import Path
from sqlalchemy import text, insert
from tweepy.asynchronous import AsyncClient

from restweetution import config_loader
from restweetution.collection import CollectionTree
from restweetution.collectors.clients.client import Client
from restweetution.models.storage.queries import CollectionQuery, TweetFilter, TweetQuery
from restweetution.models.twitter import Media
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.extractor import Extractor
from restweetution.storages.postgres_jsonb_storage.models import TEST
import sqlite3

elastic: ElasticStorage


async def main():
    global elastic

    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
    storage = conf.build_storage()
    extractor = Extractor(storage)
    query = CollectionQuery()
    query.offset = 0
    query.direct_hit = True
    res = await storage.get_linked_tweets(query)
    await extractor.tweet_load_all(res)


    for tweet in res:
        if tweet.tweet.get_media_keys():
            print([m.get_url() for m in tweet.get_media()])
    #     if tweet.get_quoted_tweet():
    #         print('=========')
    #         print(tweet.get_quoted_tweet().id, tweet.get_quoted_tweet().text)
    #         print(tweet.tweet.id, tweet.tweet.text)
    print(len([t for t in res if t.tweet.get_media_keys()]))
    # print(len(new))
    # print(new)

    # async with storage.get_engine().begin() as conn:
    #     stmt = insert(TEST)
    #     await conn.execute(stmt, [{'id': 945678901234567891}])
    #     await conn.commit()
    #
    # if True:
    #     return

    # await storage.build_tables()

    # client = Client(bearer_token=token, return_type=aiohttp.ClientResponse)
    #
    # await client.get_quote_tweets(exclude='retweets', id='1616893127310315525')
    # [print(r, r.time_to_reset()) for r in list(client.rates.values())]
    # # print(res)

    # query = CollectionQuery()
    # # query.rule_ids = [1201, 1200]
    # filter_ = TweetFilter(media=True)
    # res = await storage.query_tweets(query=query, filter_=filter_)
    #
    # extractor = Extractor(storage)
    # collection = await extractor.collection_from_tweets(res)
    #
    # print(len(collection.tweets), len(collection.medias), len(collection.rules))
    # # print(collection.rules)
    # tree = CollectionTree(collection=collection)
    #
    # for k, m in collection.medias.items():
    #     media = tree.get_media(k)
    #     for r in media.rules():
    #         print(r.id)

    # print(res[0].tweet.attachments.media_keys)
    # ids = [r.tweet_id for r in res]
    # id_count = defaultdict(int)
    # for i in ids:
    #     id_count[i] += 1
    #
    # print(len(res))
    # print(len(id_count.keys()))

    # dd = PhotoDownloader(root='/Users/david/Movies')
    # dd.download(url='https://video.twimg.com/ext_tw_video/1609578504491831297/pu/vid/1280x720/MhDCilqRHCo5ztI7.mp4?tag=12')
    # await dd.wait_finish()

    # server = SSHTunnelForwarder(('ceres.huma-num.fr', 22),
    #                             ssh_private_key=r'/Users/david/.ssh/id_ed25519',
    #                             ssh_username="davidg",
    #                             remote_bind_address=('127.0.0.1', 5432),
    #                             # logger=create_logger(loglevel=1)  # Makes processes being ran displayed
    #                             )
    # server.start()
    #
    # storage = conf.build_storage()
    #
    # old = time.time()
    # old_big = 0
    # b_count = 0
    # async for res in storage.get_collected_tweets_stream(rule_ids=[78]):
    #     print(f'time: {time.time() - old}')
    #     for i in range(len(res)-1):
    #         if res[i].tweet.created_at > res[i+1].tweet.created_at:
    #             b_count = b_count + 1
    #             print(f'bigger: {b_count}')
    #
    #     old = time.time()

    # server.stop()

    # postgres = conf.build_storage()
    # elastic = conf.build_elastic_exporter()
    # extractor = Extractor(postgres)
    #
    # csv = CSVExporter('tweet', '/Users/david/Restweetution/csv_dump')
    #
    # date_from = datetime.datetime(2021, 9, 1, 0, 0, tzinfo=datetime.timezone.utc)
    # date_to = datetime.datetime(2022, 6, 1, 0, 0, tzinfo=datetime.timezone.utc)
    # rule_ids = [2]
    #
    # res = await postgres.get_collected_tweets(rule_ids=rule_ids)
    # bulk = await extractor.expand_collected_tweets(res)
    #
    # view_exporter = ViewExporter(TweetView(), csv)
    # await view_exporter.export(bulk_data=bulk, key='felix-sha1s', only_ids=[r.tweet_id for r in res], fields=['media_sha1s'])


asyncio.run(main())
