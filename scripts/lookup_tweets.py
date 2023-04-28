import asyncio
import datetime
import logging
import os
from collections import defaultdict
from typing import List

from tweepy.asynchronous import AsyncClient

from restweetution import config_loader
from restweetution.models.config.query_fields_preset import ALL_CONFIG
from restweetution.models.rule import RuleMatch
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.queries import CollectionQuery
from restweetution.models.twitter import Tweet
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.utils import fire_and_forget

elastic: ElasticStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger('Lookup')

total = 0
total_found = 0
total_missing = 0


async def main():
    global elastic
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))

    storage = conf.build_storage()
    # token = await storage.get_token('david')

    restweet_users = await storage.get_restweet_users()

    clients = [
        AsyncClient(bearer_token=u.bearer_token, return_type=dict, wait_on_rate_limit=True)
        for u in restweet_users
    ]

    client_running_status = {c.bearer_token: False for c in clients}

    query = CollectionQuery()
    # query.rule_ids = [428, 483, 553, 482, 405, 413, 415, 404, 414, 392, 403, 406, 412, 566, 700]
    query.rule_ids = []
    async for data in storage.get_rule_matches_stream(query.rule_ids, chunk_size=100):
        try:
            while True:
                available_clients = [c for c in clients if not client_running_status[c.bearer_token]]
                if not available_clients:
                    print('all clients sleeping.. wait 10s')
                    await asyncio.sleep(10)
                else:
                    client = available_clients[0]
                    client_running_status[client.bearer_token] = True
                    fire_and_forget(check_tweets(client, storage, data, client_running_status))
                    break
        except Exception as e:
            logger.error(e)


async def check_tweets(client: AsyncClient, storage, data: List[RuleMatch], status):
    global total, total_found, total_missing
    try:
        tweet_ids = list({m.tweet_id for m in data})
        db_tweets = await storage.get_tweets(ids=tweet_ids)

        to_ignore = await storage.get_custom_datas('check_missing', ids=tweet_ids)
        ignore_ids = {d.id for d in to_ignore}
        tweet_ids = [t for t in tweet_ids if t not in ignore_ids]
        if not tweet_ids:
            status[client.bearer_token] = False
            logger.info('already checked; continue')
            return

        raw_res = await client.get_tweets(tweet_ids, **ALL_CONFIG.twitter_format())
        tweets = [Tweet(**d) for d in raw_res['data']]
        if not tweets:
            status[client.bearer_token] = False
            return
        existing_ids = {t.id for t in tweets}
        missing_ids = set(tweet_ids) - existing_ids
        user_to_check = defaultdict(list)
        tweet_status = {t.id: 'alive' for t in tweets}
        # db_tweets = {t.id: t for t in data.get_tweets()}

        if 'errors' in raw_res:
            for error in raw_res['errors']:
                tweet_id = error['resource_id']
                if 'not-found' in error['type']:
                    tweet_status[tweet_id] = "deleted"
                else:
                    tweet_status[tweet_id] = "unknown"
                    if tweet_id in db_tweets:
                        user_to_check[db_tweets[tweet_id].author_id].append(tweet_id)
        user_to_check_ids = list(user_to_check.keys())
        if user_to_check_ids:
            users_res = await client.get_users(ids=user_to_check_ids,
                                               user_fields=ALL_CONFIG.twitter_format()['user_fields'])

            if 'data' in users_res:
                for user in users_res['data']:
                    user_id = user['id']
                    if 'protected' in user and user['protected']:
                        for t in user_to_check[user_id]:
                            tweet_status[t] = 'protected'

            if 'errors' in users_res:
                for error in users_res['errors']:
                    user_id = error['resource_id']
                    detail = error['detail']
                    if 'suspended' in detail:
                        for t in user_to_check[user_id]:
                            tweet_status[t] = 'suspended'
                    else:
                        for t in user_to_check[user_id]:
                            tweet_status[t] = 'deleted_account'

        await storage.save_tweets(tweets)

        timestamp = datetime.datetime.now()
        custom_key = "check_missing"
        deleted_datas = [CustomData(id=t_id, key=custom_key,
                                    data={"deleted": True, "reason": tweet_status[t_id], "timestamp": timestamp})
                         for
                         t_id in missing_ids]
        if deleted_datas:
            await storage.save_custom_datas(deleted_datas, override=False)

        existing_datas = [CustomData(id=t_id, key=custom_key, data={"exist": True, "timestamp": timestamp}) for t_id
                          in
                          existing_ids]
        if existing_datas:
            await storage.save_custom_datas(existing_datas, override=True)

        total += len(tweet_ids)
        total_found += len(existing_ids)
        total_missing += len(missing_ids)
        logger.info(f'total: {total}  found[{total_found}]  missing[{total_missing}]  ignored[{len(ignore_ids)}]')
    except Exception as e:
        logger.error(e)
    status[client.bearer_token] = False


asyncio.run(main())
