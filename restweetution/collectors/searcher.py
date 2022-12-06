import asyncio
import datetime
import logging
import math
import time
import traceback
from typing import Callable, List, Optional

import aiohttp
import tweepy.errors
from tweepy.asynchronous import AsyncClient

from restweetution.collectors.response_parser import parse_includes
from restweetution.models.bulk_data import BulkData
from restweetution.models.config.tweet_config import QueryFields
from restweetution.models.rule import Rule
from restweetution.models.searcher import CountResponse, LookupResponseUnit, LookupResponse, TweetPyLookupResponse, \
    SearcherConfig, TimeWindow
from restweetution.models.twitter import Tweet, Includes, User
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage
from restweetution.utils import Event

from restweetution.models.config.user_config import RuleConfig

logger = logging.getLogger('Searcher')


class Searcher:
    def __init__(self, storage: PostgresStorage, bearer_token):
        super().__init__()

        self.storage = storage
        self._client = AsyncClient(bearer_token=bearer_token, return_type=aiohttp.ClientResponse)

        self._config = SearcherConfig()

        self._collect_task: Optional[asyncio.Task] = None

        self.event_update: Event = Event()

    def start_collection(self):
        if self.is_running():
            raise Exception('Searcher Collect Task already Running')
        self._collect_task = asyncio.create_task(self.count_and_collect())
        return self._collect_task

    def stop_collection(self):
        if self._collect_task:
            self._collect_task.cancel()
            self._collect_task = None

    def is_running(self):
        return self._collect_task is not None and not self._collect_task.done()

    async def set_rule(self, rule: RuleConfig):
        rule = Rule(query=rule.query, tag=rule.tag)
        res = await self.storage.request_rules([rule])
        if res:
            self._config.set_rule(res[0])

        return self.get_rule()

    async def set_config(self, config: SearcherConfig):
        if config.rule:
            await self.set_rule(RuleConfig(tag=config.rule.tag, query=config.rule.query))
        self._config = config

    def set_time_window(self, start: datetime = None, end: datetime = None):
        if self.is_running():
            raise Exception('Cannot change time frame during collection. please use stop_collection() first')
        self._config.time_window = TimeWindow(start=start, end=end)
        self._config.reset_counters()

    def get_config(self):
        return self._config

    def remove_rule(self):
        self._config.set_rule(None)
        if self.is_running():
            self.stop_collection()

    def get_rule(self):
        return self._config.rule

    def get_time_params(self):
        params = {}

        start = self._config.time_window.start
        if start:
            params['start_time'] = start
        end = self._config.time_window.end
        if end:
            params['end_time'] = time
        cursor = self._config.time_window.cursor
        if cursor:
            params['until_id'] = cursor

        return params

    async def collect(self):
        logger.info('Start Searcher')

        if not self._config.rule:
            raise Exception('The streamer has no rule to collect. Use set_rule()')

        params = self.get_time_params()

        search_function = self._client.search_recent_tweets if self._config.recent else self._client.search_all_tweets

        rule = self._config.rule
        fields = self._config.fields.twitter_format()
        query = rule.query
        max_results = self._config.max_results

        logger.info(f'time params: {params}')

        async for res in self._token_loop(search_function, query, **fields, max_results=max_results,  **params):
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

                logger.info(f'Received: {len(bulk_data.get_tweets())} tweets')
                await self.storage.save_bulk(bulk_data)

                smallest_id = min([int(id_) for id_ in direct_ids])
                self._config.time_window.cursor = str(smallest_id)
                self._config.collected_count += len(direct_ids)
                asyncio.create_task(self.event_update(self._config))

            except Exception as e:
                logger.warning(traceback.format_exc())
                logger.warning(e)

    async def get_collect_count(self):
        if not self._config.rule:
            raise Exception('No rule set on Streamer, cannot count. Use set_rule()')
        logger.info('Start Count...')
        recent = self._config.recent
        query = self._config.rule.query
        params = self.get_time_params()
        count_func: Callable = self._client.get_recent_tweets_count if recent else self._client.get_all_tweets_count

        total_count = 0
        async for res in self._token_loop(count_func, query=query, **params):
            count = CountResponse(**res.dict())
            total_count += count.meta.total_tweet_count
            self._config.total_count = total_count

        asyncio.create_task(self.event_update(self._config))
        logger.info(f'Found {total_count} tweets to collect')
        return total_count

    async def count_and_collect(self):
        if not self._config.has_count():
            await self.get_collect_count()
        await self.collect()

    async def get_tweets_as_stream(self, ids: List[str], fields: QueryFields = None, max_per_loop: int = 100):
        if not fields:
            fields = self._config.fields

        async for res in self._lookup_loop(
                lookup_function=self._ids_lookup,
                get_function=self._client.get_tweets,
                values=ids,
                fields=fields.twitter_format(),
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
            fields = self._config.fields

        result = LookupResponse(requested=ids)
        async for res in self.get_tweets_as_stream(ids=ids, fields=fields, max_per_loop=max_per_loop):
            result += res
        return result

    async def get_users(self, ids: List[str] = None, usernames: List[str] = None, fields: QueryFields = None, **kwargs):
        if not ids and not usernames:
            return
        if not fields:
            fields = self._config.fields

        result = LookupResponse()
        async for res in self.get_users_as_stream(ids=ids, usernames=usernames, fields=fields, **kwargs):
            result += res
        return result

    async def get_users_as_stream(self, ids: List[str] = None, usernames: List[str] = None, fields: QueryFields = None,
                                  max_per_loop: int = 100):

        if not ids and not usernames:
            return
        if not fields:
            fields = self._config.fields

        lookup_function = self._ids_lookup if ids else self._usernames_lookup
        values = ids if ids else usernames

        async for res in self._lookup_loop(
                lookup_function=lookup_function,
                get_function=self._client.get_users,
                values=values,
                fields=fields.twitter_format(),
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
