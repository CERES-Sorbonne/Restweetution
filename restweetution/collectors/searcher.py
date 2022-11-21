import asyncio
import datetime
import logging
import math
import time
from typing import Callable, List

import aiohttp
import tweepy.errors
from tweepy.asynchronous import AsyncClient

from restweetution.collectors.response_parser import parse_includes
from restweetution.models.bulk_data import BulkData
from restweetution.models.config.tweet_config import QueryFields
from restweetution.models.rule import SearcherRule
from restweetution.models.searcher import CountResponse, LookupResponseUnit, LookupResponse, TweetPyLookupResponse
from restweetution.models.twitter import Tweet, Includes, User
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logger = logging.getLogger('Searcher')


class Searcher:
    def __init__(self, storage: PostgresStorage, bearer_token, fields: QueryFields = None, **kwargs):
        super().__init__()

        self.storage = storage
        self._client = AsyncClient(bearer_token=bearer_token, return_type=aiohttp.ClientResponse, **kwargs)
        self._default_fields = fields if fields else QueryFields()

    async def collect(self, rule: SearcherRule, fields: QueryFields = None, recent=True, max_results=10,
                      count_tweets=True, **kwargs):
        logger.info('Start search loop')

        res = await self.storage.request_rules([rule])
        rule = res[0]

        query = rule.query

        if count_tweets:
            count = await self.get_tweets_count(query, recent=recent, granularity='day', **kwargs)
            logger.info(f'Retrieving {count} tweets')

        if not fields:
            fields = self._default_fields

        search_function = self._client.search_recent_tweets if recent else self._client.search_all_tweets

        async for res in self._token_loop(search_function, query, **fields.dict(), max_results=max_results, **kwargs):
            try:
                bulk_data = BulkData()
                tweets = [Tweet(**t) for t in res.data]
                bulk_data.add_tweets(tweets)

                includes = Includes(**res.includes)
                bulk_data.add(**parse_includes(includes))

                # set collected tweets to rule
                collected_at = datetime.datetime.now()
                # use copy of rule to avoid polluting global object
                rule_copy = rule.copy()

                direct_ids = [t.id for t in tweets]
                includes_ids = [t.id for t in includes.tweets]

                rule_copy.add_direct_tweets(tweet_ids=direct_ids, collected_at=collected_at)
                if includes_ids:
                    rule_copy.add_includes_tweets(tweet_ids=includes_ids, collected_at=collected_at)

                bulk_data.add_rules([rule_copy])

                logger.info(f'Save: {len(bulk_data.get_tweets())} tweets')
                await self.storage.save_bulk(bulk_data)
            except Exception as e:
                logger.warning(e)

    async def get_tweets_count(self, query, recent=True, **kwargs):
        count_func: Callable = self._client.get_recent_tweets_count if recent else self._client.get_all_tweets_count

        total_count = 0
        async for res in self._token_loop(count_func, query=query, **kwargs):
            count = CountResponse(**res.dict())
            total_count += count.meta.total_tweet_count

        return total_count

    async def get_tweets_as_stream(self, ids: List[str], fields: QueryFields = None, max_per_loop: int = 100):
        if not fields:
            fields = self._default_fields

        async for res in self._lookup_loop(
                lookup_function=self._ids_lookup,
                get_function=self._client.get_tweets,
                values=ids,
                fields=fields.dict(),
                max_per_loop=max_per_loop
        ):
            result = LookupResponse(
                requested=res.requested,
                missing=res.missing,
                errors=res.errors,
                meta=res.meta
            )

            tweets = [Tweet(**t) for t in res.data]
            result.bulk_data.add_tweets(tweets)
            result.bulk_data.add(**parse_includes(Includes(**res.includes)))

            yield result

    async def get_tweets(self, ids: List[str], fields: QueryFields = None, max_per_loop: int = 100):
        if not ids:
            return
        if not fields:
            fields = self._default_fields

        result = LookupResponse(requested=ids)
        async for res in self.get_tweets_as_stream(ids=ids, fields=fields, max_per_loop=max_per_loop):
            result += res
        return result

    async def get_users(self, ids: List[str] = None, usernames: List[str] = None, fields: QueryFields = None, **kwargs):
        if not ids and not usernames:
            return
        if not fields:
            fields = self._default_fields

        result = LookupResponse()
        async for res in self.get_users_as_stream(ids=ids, usernames=usernames, fields=fields, **kwargs):
            result += res
        return result

    async def get_users_as_stream(self, ids: List[str] = None, usernames: List[str] = None, fields: QueryFields = None,
                                  max_per_loop: int = 100):

        if not ids and not usernames:
            return
        if not fields:
            fields = self._default_fields

        lookup_function = self._ids_lookup if ids else self._usernames_lookup
        values = ids if ids else usernames

        async for res in self._lookup_loop(
                lookup_function=lookup_function,
                get_function=self._client.get_users,
                values=values,
                fields=fields.dict(),
                max_per_loop=max_per_loop
        ):
            result = LookupResponse(
                requested=res.requested,
                missing=res.missing,
                errors=res.errors,
                meta=res.meta
            )

            users = [User(**t) for t in res.data]
            result.bulk_data.add_users(users)
            result.bulk_data.add(**parse_includes(Includes(**res.includes)))

            yield result

    @staticmethod
    async def _token_loop(get_function: Callable, query: str, **kwargs):
        next_token = None
        running = True
        while running:
            try:
                if next_token:
                    resp = await get_function(query=query, next_token=next_token, **kwargs)
                else:
                    resp = await get_function(query=query, **kwargs)
            except tweepy.errors.TooManyRequests:
                logger.info('Unexpected TooManyRequest, sleep for 15min')
                await asyncio.sleep(15 * 60)
                continue

            async with resp:
                res = TweetPyLookupResponse(**await resp.json())

            if res.meta and 'next_token' in res.meta:
                next_token = res.meta['next_token']
            else:
                next_token = None
            running = next_token

            rate_limit_remaining = int(resp.headers.get('x-rate-limit-remaining'))
            rate_limit_reset = int(resp.headers.get('x-rate-limit-reset'))
            if rate_limit_remaining == 0:
                wait_duration = rate_limit_reset - math.floor(time.time())
                logger.info('sleep for ', str(wait_duration), ' seconds')
                await asyncio.sleep(wait_duration)

            yield res

    # @staticmethod
    # def parse_headers(resp: aiohttp.ClientResponse):

    @staticmethod
    async def _lookup_loop(lookup_function: Callable, get_function: Callable, values: List, fields: dict,
                           max_per_loop: int = 100):
        if not values:
            return
        final_stop = len(values)

        for step in range(0, final_stop, max_per_loop):
            stop = min(step + max_per_loop, final_stop)
            values_slice = values[step:stop]
            yield await lookup_function(get_function=get_function, values=values_slice, **fields)

    @staticmethod
    async def _ids_lookup(get_function: Callable, values: List[str], **fields):
        if not values:
            return
        ids = values

        res = await get_function(ids=ids, **fields)
        missing = set(ids)
        datas = res.data if res.data else []
        for data in datas:
            id_str = str(data['id'])
            if id_str in missing:
                missing.remove(id_str)

        return LookupResponseUnit(
            data=datas,
            includes=res.includes,
            errors=res.errors,
            meta=res.meta,
            requested=ids,
            missing=missing
        )

    @staticmethod
    async def _usernames_lookup(get_function: Callable, values: List[str], **fields):
        if not values:
            return
        usernames = values

        res = await get_function(usernames=usernames, **fields)
        missing = set(usernames)
        datas = res.data if res.data else []
        for data in datas:
            id_str = str(data['username'])
            if id_str in missing:
                missing.remove(id_str)

        return LookupResponseUnit(
            data=datas,
            includes=res.includes,
            errors=res.errors,
            meta=res.meta,
            requested=usernames,
            missing=missing
        )
