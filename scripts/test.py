import asyncio
import datetime
import os
import time
from random import random

import asyncpg
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sshtunnel import SSHTunnelForwarder, create_logger

from restweetution import config_loader
from restweetution.errors import ResponseParseError
from restweetution.models.bulk_data import BulkData
from restweetution.models.config.downloaded_media import DownloadedMedia
from restweetution.models.config.user_config import UserConfig
from restweetution.models.rule import Rule
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.error import ErrorModel
from restweetution.models.twitter import Tweet
from restweetution.storages.postgres_jsonb_storage.helpers import find_fields
from restweetution.storages.postgres_jsonb_storage.models import meta_data, TWEET, COLLECTED_TWEET
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage
from restweetution.utils import clean_dict


async def main():
    # main_conf = config_loader.get_config_from_file(os.getenv('CONFIG'))
    # storage = main_conf.storage
    postgres = PostgresJSONBStorage("postgresql+asyncpg://localhost/postgres")
    # await postgres.build_tables()
    # await postgres.build_tables()

    old = time.time()
    res = await postgres.get_tweets_with_media_keys(media_keys=['3_1605330589456166912', '3_1605330606350540803'])
    print(time.time() - old)
    print(len(res))
    # print(res.referenced_tweets)

    # res = await postgres.get_medias()
    # print(res)
    # dmedias = [DownloadedMedia(sha1='lala', format='jpg', **m.dict()) for m in res[0:4]]
    # await postgres.save_downloaded_medias(dmedias)
    # res = await postgres.get_downloaded_medias(media_keys=['3_1602863148742381568', '7_1596909772770795523'], urls=['https://pbs.twimg.com/media/Fj6DFNbaMAE0Uvf.jpg'], is_and=False)
    # for r in res:
    #     print(r)


    # old = time.time()
    # tweets = await postgres.get_tweets(fields=['entities'])
    # print(f'Get tweets took: {time.time() - old} seconds')
    # print(find_fields(tweets))
    #
    # t = TWEET.primary_key
    # print([a.name for a in t])

    # tweets = await storage.get_tweets(ids=[
    #     "1599536031090483200",
    #     "1599536030381527040",
    #     "1599536029836668928",
    #     "1599536028263780352",
    #     "1599536028087222272",
    #     "1600257492902023168",
    #     "1599536026888077312",
    #     "1599536026774491136",
    #     "1599536026757627904",
    #     "1599536024928997376",
    #     "1599536024173936640",
    #     "1599536022991253504",
    #     "1599536021959368705",
    #     "1599536021422895105"])
    # print('got tweets: ', str(len(tweets)))
    #
    # old = time.time()
    # await postgres.save_tweets(tweets)
    # print(f'save tweets took: {time.time() - old} seconds')

    # # tweets = tweets[0:200]
    # old = time.time()
    # tweets = [t.__dict__ for t in tweets]
    # print(f'converting to dict took: {time.time() - old} seconds')
    #
    # old = time.time()
    # t_dicts = [clean_dict(t) for t in tweets]
    # print(f'converting to clean dict took: {time.time() - old} seconds')
    #
    # old = time.time()
    # keys = set()
    # for dico in t_dicts:
    #     keys.update(list(dico.keys()))
    #
    # print(f'collecting keys took: {time.time() - old} seconds')
    #
    # print(keys)

    # datas = await postgres.get_custom_datas(key='test')
    # print(datas)

    # data = CustomData(id='1', key='test', data=['lolipop', 'canaille', datetime.datetime.now()])
    # await postgres.save_custom_datas([data])

    # rules = [Rule(tag=str(9-i), query='query: ' + str(i)) for i in range(5)]
    # res = await postgres.request_rules(rules, True)
    # print(res)
    # try:
    #     raise ResponseParseError('lalalala', data=dict(bon='bahvoila'))
    # except ResponseParseError as e:
    #     error = ErrorModel(error=e)
    #     await postgres.save_error(error)

    # users = await storage.get_user_configs()
    # print(len(users))
    # user.streamer_state.updated_at = datetime.datetime.now()
    # await postgres.save_restweet_user(user)

    # await postgres.update_restweet_user(users)

    # old = time.time()
    # res = await storage.get_tweets()
    # print('get took: ', str(time.time() - old))
    # print(len(res))
    #
    # old = time.time()
    # await storage.save_tweets(res[0:1000])
    # print('insert took: ', str(time.time() - old))
    # engine = create_async_engine("postgresql+asyncpg://localhost/postgres", echo=False)
    # async with engine.begin() as conn:
    #     await conn.run_sync(meta_data.drop_all)
    #     await conn.run_sync(meta_data.create_all)
    #
    #     # stmt = insert(tweet)
    #     # stmt = stmt.on_conflict_do_update(
    #     #     index_elements=['id'],
    #     #     set_=dict(tweet.c)
    #     # )
    #     # old = time.time()
    #     # await conn.execute(stmt, [r.dict() for r in res])
    #     # print('insert took: ', str(time.time() - old))
    #
    #     stmt = select(TWEET)
    #     old = time.time()
    #     await conn.execute(stmt)
    #     print('JSON get took: ', str(time.time() - old))
    #     #
    #     # keys = list(res.keys())
    #     #
    #     # def to_dict(row):
    #     #     return {keys[i]: row[i] for i in range(len(keys))}
    #     #
    #     # res = [to_dict(r) for r in res]
    #     # print('JSON with Dict building: ', str(time.time() - old))
    #     # # print(res[0])
    #     #
    #     # res = [Tweet(**r) for r in res]
    #     # print('JSON with Tweet(BaseModel) building: ', str(time.time() - old))
    #     #
    #     # res = res[0:1000]
    #     # old = time.time()
    #     # stmt = insert(tweet)
    #     # stmt = stmt.on_conflict_do_update(
    #     #     index_elements=['id'],
    #     #     set_=dict(tweet.c)
    #     # )
    #     # await conn.execute(stmt, [r.dict() for r in res])
    #     # print('JSON DB insert took (1000 rows): ', str(time.time() - old))
    #     #
    #     # old = time.time()
    #     # await storage.save_tweets(res[0:1000])
    #     # print('Old DB insert took (1000 rows): ', str(time.time() - old))
    #
    #     # print(res[0])
    #     # print(len(res.fetchall()))
    # async with engine.begin() as conn:
    #     stmt = select(TWEET)
    #     old = time.time()
    #     await conn.execute(stmt)
    #     print('JSON get took: ', str(time.time() - old))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
