import logging
from typing import Callable, List, Dict

from tweepy.asynchronous import AsyncClient

from restweetution.collectors.response_parser import parse_includes
from restweetution.models.bulk_data import BulkData
from restweetution.models.config.tweet_config import QueryFields
from restweetution.models.rule import SearcherRule
from restweetution.models.searcher import CountResponse, LookupResponseUnit, LookupResponse
from restweetution.models.twitter import Tweet, Includes, User
from restweetution.storage_manager import StorageManager


class Searcher:
    def __init__(self, storage: StorageManager, bearer_token, fields: QueryFields = None, **kwargs):
        super().__init__()

        self.storage_manager = storage
        self._logger = logging.getLogger('Searcher')
        self._client = AsyncClient(bearer_token=bearer_token, **kwargs)
        self._default_fields = fields if fields else QueryFields()

    async def collect(self, rule: SearcherRule, fields: QueryFields = None, recent=True, max_results=10, **kwargs):
        self._logger.info('Start search loop')

        res = await self.storage_manager.request_rules([rule])
        rule = res[0]

        query = rule.query

        count = await self.get_tweets_count(query, recent=recent, **kwargs)
        self._logger.info(f'Retrieving {count.meta.total_tweet_count} tweets')

        if not fields:
            fields = self._default_fields

        search_function = self._client.search_recent_tweets if recent else self._client.search_all_tweets

        async for res in self._token_loop(search_function, query, **fields.dict(), max_results=max_results, **kwargs):
            try:
                bulk_data = BulkData()

                tweets = [Tweet(**t) for t in res.data]
                bulk_data.add_tweets(tweets)
                bulk_data.add(**parse_includes(Includes(**res.includes)))
                bulk_data.add_rules([rule.copy()], collected=True)

                self._logger.info(f'Save: {len(bulk_data.get_tweets())} tweets')
                self.storage_manager.save_bulk(bulk_data)
            except Exception as e:
                self._logger.warning(e)

    async def get_tweets_count(self, query, recent=True, **kwargs):
        count_func: Callable = self._client.get_recent_tweets_count if recent else self._client.get_all_tweets_count

        res = await count_func(query, **kwargs)
        count = CountResponse(data=res.data, meta=res.meta, errors=res.errors, includes=res.includes)
        return count

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
            if next_token:
                res = await get_function(query=query, next_token=next_token, **kwargs)
            else:
                res = await get_function(query=query, **kwargs)
            next_token = res.meta['next_token']
            running = next_token
            yield res

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
