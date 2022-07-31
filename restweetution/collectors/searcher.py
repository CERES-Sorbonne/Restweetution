import logging
from typing import Callable, List, Dict

from tweepy.asynchronous import AsyncClient

from restweetution.collectors.response_parser import parse_includes
from restweetution.models.bulk_data import BulkData
from restweetution.models.searcher import CountResponse, LookupResponseUnit, LookupResponse
from restweetution.models.twitter import RestTweet, TweetIncludes
from restweetution.storage_manager import StorageManager


class Searcher:
    def __init__(self, storage: StorageManager, bearer_token, fields: Dict = None, **kwargs):
        super().__init__()

        self.storage_manager = storage
        self._logger = logging.getLogger('Searcher')
        self._client = AsyncClient(bearer_token=bearer_token, **kwargs)
        self._default_fields = fields if fields else {}

    async def collect_recent(self, query: str, fields: dict = None, tags: List[str] = None, **kwargs):
        self._logger.info('Start search loop')

        count = await self.get_tweets_count(query, **kwargs)
        self._logger.info(f'Retrieving {count.meta.total_tweet_count} tweets')

        if not fields:
            fields = self._default_fields
        if not tags:
            tags = []

        async for res in self._token_loop(self._client.search_recent_tweets, query, **fields, **kwargs):
            bulk_data = BulkData()

            tweets = [RestTweet(**t) for t in res.data]
            bulk_data.add_tweets(tweets)
            bulk_data.add(**parse_includes(TweetIncludes(**res.includes)))

            self._logger.info(f'Save: {len(bulk_data.get_tweets())} tweets')
            self.storage_manager.save_bulk(bulk_data, tags)

    async def get_tweets_count(self, query, **kwargs):
        res = await self._client.get_recent_tweets_count(query, **kwargs)
        count = CountResponse(data=res.data, meta=res.meta, errors=res.errors, includes=res.includes)
        return count

    async def get_tweets_stream(self, ids: List[str], fields: dict = None, max_per_loop: int = 100):
        if not fields:
            fields = self._default_fields

        async for res in self._lookup_loop(self._client.get_tweets, ids=ids, fields=fields, max_per_loop=max_per_loop):
            result = LookupResponse(requested_ids=res.requested_ids,
                                    missing_ids=res.missing_ids,
                                    errors=res.errors,
                                    meta=res.meta)

            tweets = [RestTweet(**t) for t in res.data]
            result.bulk_data.add_tweets(tweets)
            result.bulk_data.add(**parse_includes(TweetIncludes(**res.includes)))

            yield result

    async def get_tweets(self, ids: List[str], fields: dict = None, max_per_loop: int = 100):
        if not fields:
            fields = self._default_fields
        result = LookupResponse(requested_ids=ids)
        async for res in self.get_tweets_stream(ids=ids, fields=fields, max_per_loop=max_per_loop):
            result.bulk_data += res.bulk_data
            result.missing_ids.extend(res.missing_ids)
            result.errors.extend(res.errors)
            result.meta.update(res.meta)
        return result

    #
    # async def get_users(self, ids: List[str], fields: dict = None, max_per_loop: int = 100):
    #     if not fields:
    #         fields = {}
    #     return self._lookup_loop(self._client.get_users, ids=ids, fields=fields, max_per_loop=max_per_loop)

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
    async def _lookup_loop(get_function: Callable,
                           ids: List[str],
                           fields: dict,
                           max_per_loop: int = 100):
        if not ids:
            return
        if not fields:
            fields = {}

        final_stop = len(ids)

        for step in range(0, final_stop, max_per_loop):
            stop = min(step + max_per_loop, final_stop)
            ids_slice = ids[step:stop]
            res = await get_function(ids=ids_slice, **fields)

            missing = set(ids_slice)
            datas = res.data if res.data else []
            for data in datas:
                id_str = str(data['id'])
                if id_str in missing:
                    missing.remove(id_str)

            yield LookupResponseUnit(data=datas,
                                     includes=res.includes,
                                     errors=res.errors,
                                     meta=res.meta,
                                     requested_ids=ids_slice,
                                     missing_ids=list(missing))
