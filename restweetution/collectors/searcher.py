import asyncio
import logging
import math
import time
import traceback
from datetime import datetime
from typing import Callable, List, Optional

import aiohttp
import tweepy.errors
from tweepy.asynchronous import AsyncClient

from restweetution.collectors.response_parser import parse_includes
from restweetution.models.bulk_data import BulkData
from restweetution.models.config.query_fields import QueryFields
from restweetution.models.config.query_fields_preset import ALL_CONFIG
from restweetution.models.config.user_config import RuleConfig
from restweetution.models.rule import Rule
from restweetution.models.searcher import CountResponse, LookupResponseUnit, LookupResponse, TweetPyLookupResponse, \
    TimeWindow
from restweetution.models.twitter import Tweet, Includes, User
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage
from restweetution.utils import AsyncEvent, fire_and_forget

logger = logging.getLogger('Searcher')


class Searcher:
    def __init__(self, storage: PostgresJSONBStorage, bearer_token):
        super().__init__()

        self.storage = storage
        self._client = AsyncClient(bearer_token=bearer_token, return_type=aiohttp.ClientResponse)

        self._rule: Optional[Rule] = None
        self._fields: QueryFields = ALL_CONFIG
        self._time_window = TimeWindow()
        self._max_results = 100

        self._collect_task: Optional[asyncio.Task] = None

        self.event_update: AsyncEvent = AsyncEvent()
        self.event_stop = AsyncEvent()
        self.event_collect = AsyncEvent()

        self._running = False
        self._sleeping = False

    def start_collection(self):
        if self.is_running():
            raise Exception('Searcher Collect Task already Running')
        self._collect_task = asyncio.create_task(self.count_and_collect())
        self._running = True
        return self._collect_task

    def stop_collection(self):
        if self._collect_task:
            self._collect_task.cancel()
            self._collect_task = None
        self._running = False

    def is_running(self):
        return self._collect_task is not None and not self._collect_task.done() and self._running

    def is_sleeping(self):
        return self.is_running() and self._sleeping

    async def set_rule(self, rule: RuleConfig):
        if self._rule and rule.query == self._rule.query:
            return
        rule = Rule(query=rule.query, tag=rule.tag)
        res = await self.storage.request_rules([rule])
        if res:
            self._rule = res[0]
            self._time_window.reset_cursor()

        return self.get_rule()

    def set_fields(self, fields: QueryFields):
        if self.is_running():
            raise Exception('Cannot change fields during collection. Please use stop_collection() before')
        self._fields = fields

    def get_fields(self):
        return self._fields

    def load_time_window(self, time_window: TimeWindow):
        if self.is_running():
            raise Exception('Cannot load time window if searcher is running')
        self._time_window = time_window

    def set_time_window(self, start: datetime, end: datetime, recent=True):
        if self.is_running():
            raise Exception('Cannot change time_window during collection. Please use stop_collection() before')
        if self._time_window.start == start and self._time_window.end == end and self._time_window.recent == recent:
            return

        self._time_window = TimeWindow(start=start, end=end, recent=recent)

    def get_time_window(self):
        return self._time_window

    def remove_rule(self):
        self._rule = None
        self._time_window.reset_cursor()
        if self.is_running():
            self.stop_collection()

    def get_rule(self):
        return self._rule

    def get_search_time_params(self):
        params = {}
        start = self._time_window.start
        end = self._time_window.end
        cursor = self._time_window.cursor
        if start:
            params['start_time'] = start
        if cursor:
            params['end_time'] = cursor
        elif end:
            params['end_time'] = end
        return params

    def get_count_time_params(self):
        params = {'granularity': 'day'}
        end = self._time_window.end
        start = self._time_window.start
        if start:
            params['start_time'] = start
        if end:
            params['end_time'] = end
        return params

    @staticmethod
    def _build_count_params(start: datetime = None, end: datetime = None, granularity: str = None):
        if granularity is None:
            granularity = 'day'

        params = {'granularity': granularity}
        if start:
            params['start_time'] = start
        if end:
            params['end_time'] = end
        return params

    async def collect(self):
        logger.info('Start Searcher')

        if not self._rule:
            raise Exception('The streamer has no rule to collect. Use set_rule()')

        params = self.get_search_time_params()
        recent = self._time_window.recent
        search_function = self._client.search_recent_tweets if recent else self._client.search_all_tweets

        rule = self._rule
        fields = self._fields.twitter_format()
        query = rule.query
        max_results = self._max_results

        logger.info(f'time params: {params}')

        async for res in self._token_loop(search_function, query, **fields, max_results=max_results, **params):
            try:
                bulk_data = BulkData()
                tweets = [Tweet(**t) for t in res.data]
                bulk_data.add_tweets(tweets)
                includes = Includes(**res.includes)

                bulk_data.add(**parse_includes(includes))

                # set collected tweets to rule
                collected_at = datetime.now()
                # use copy of rule to avoid polluting global object
                rule_copy = rule.copy()

                direct_ids = [t.id for t in tweets]
                includes_ids = [t.id for t in includes.tweets]

                rule_copy.add_direct_tweets(tweet_ids=direct_ids, collected_at=collected_at)
                if includes_ids:
                    rule_copy.add_includes_tweets(tweet_ids=includes_ids, collected_at=collected_at)

                bulk_data.add_rules([rule_copy])

                logger.info(f'Received: {len(bulk_data.get_tweets())} tweets')
                await self.storage.save_bulk(bulk_data, callback=self.event_collect)

                if 'created_at' in self._fields.tweet_fields:
                    oldest = min([bulk_data.tweets[id_].created_at for id_ in direct_ids])
                    self._time_window.cursor = oldest
                self._time_window.collected_count += len(direct_ids)
                fire_and_forget(self.event_update())

            except Exception as e:
                logger.warning(traceback.format_exc())
                logger.warning(e)

        self._running = False
        fire_and_forget(self.event_update())

    async def get_collect_count(self):
        if not self._rule:
            raise Exception('No rule set on Streamer, cannot count. Use set_rule()')
        logger.info('Start Count...')
        recent = self._time_window.recent
        query = self._rule.query
        params = self.get_count_time_params()
        count_func: Callable = self._client.get_recent_tweets_count if recent else self._client.get_all_tweets_count

        total_count = 0
        async for res in self._token_loop(count_func, query=query, **params):
            count = CountResponse(**res.dict())
            total_count += count.meta.total_tweet_count

        self._time_window.total_count = total_count
        fire_and_forget(self.event_update())
        logger.info(f'Found {total_count} tweets to collect')
        return total_count

    async def count(self, query: str, start: datetime = None, end: datetime = None, recent=True, step: str = None):
        logger.info('Start Count...')

        params = self._build_count_params(start, end, granularity=step)
        count_func: Callable = self._client.get_recent_tweets_count if recent else self._client.get_all_tweets_count

        total_count = 0
        count_units = []
        async for res in self._token_loop(count_func, query=query, **params):
            count = CountResponse(**res.dict())
            total_count += count.meta.total_tweet_count
            count_units = [*count.data, *count_units]

        return total_count, count_units

    async def collect_count_test(self):
        if not self._rule:
            raise Exception('No rule set on Streamer, cannot count. Use set_rule()')
        logger.info('Test Query and Time Window ..')
        recent = self._time_window.recent
        query = self._rule.query
        params = self.get_count_time_params()
        count_func: Callable = self._client.get_recent_tweets_count if recent else self._client.get_all_tweets_count
        await count_func(query=query, **params)
        return True

    async def count_and_collect(self):
        try:
            if not self._time_window.has_count():
                await self.get_collect_count()
            await self.collect()
        except Exception as e:
            logger.warning(e)
            raise e

    async def get_tweets_as_stream(self, ids: List[str], fields: QueryFields = None, max_per_loop: int = 100):
        if not fields:
            fields = self._fields

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
            fields = self._fields

        result = LookupResponse(requested=ids)
        async for res in self.get_tweets_as_stream(ids=ids, fields=fields, max_per_loop=max_per_loop):
            result += res
        return result

    async def get_users(self, ids: List[str] = None, usernames: List[str] = None, fields: QueryFields = None, **kwargs):
        if not ids and not usernames:
            return
        if not fields:
            fields = self._fields

        result = LookupResponse()
        async for res in self.get_users_as_stream(ids=ids, usernames=usernames, fields=fields, **kwargs):
            result += res
        return result

    async def get_users_as_stream(self, ids: List[str] = None, usernames: List[str] = None, fields: QueryFields = None,
                                  max_per_loop: int = 100):

        if not ids and not usernames:
            return
        if not fields:
            fields = self._fields

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

    async def _token_loop(self, get_function: Callable, query: str, **kwargs):
        next_token = None
        running = True
        while running:
            try:
                if next_token:
                    resp = await get_function(query=query, next_token=next_token, **kwargs)
                else:
                    resp = await get_function(query=query, **kwargs)

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
                    logger.info(f'sleep for {wait_duration} seconds')
                    self._sleeping = True
                    await asyncio.sleep(wait_duration)
                    self._sleeping = False

                yield res
            except tweepy.errors.TooManyRequests:
                logger.info('Unexpected TooManyRequest, sleep for 15min')
                self._sleeping = True
                await asyncio.sleep(15 * 60)
                self._sleeping = False
                continue
            except Exception as e:
                raise e

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
