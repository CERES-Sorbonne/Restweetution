import asyncio
import logging

from tweepy.asynchronous import AsyncClient

from restweetution.collectors.response_parser import parse_includes
from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter import RestTweet, TweetIncludes
from restweetution.storage_manager import StorageManager


class Searcher(AsyncClient):
    def __init__(self, storage: StorageManager, bearer_token=None, **kwargs):
        super().__init__(bearer_token=bearer_token, **kwargs)

        self.storage_manager = storage
        self._logger = logging.getLogger('Searcher')

    async def search_loop_recent(self, query, **kwargs):
        self._logger.info('Start search loop')

        count = await self.get_recent_tweets_count(query)
        sum_count = sum([c['tweet_count'] for c in count.data])
        self._logger.info(f'Retrieving {sum_count} tweets')

        next_token = None
        running = True
        while running:
            self._logger.info('loop')
            if next_token:
                res = await self.search_recent_tweets(query=query, next_token=next_token, **kwargs)
            else:
                res = await self.search_recent_tweets(query=query, **kwargs)

            bulk_data = BulkData()

            tweets = [RestTweet(**t) for t in res.data]
            bulk_data.add_tweets(tweets)

            parse_includes(bulk_data, (TweetIncludes(**res.includes)))

            self.storage_manager.save_bulk(bulk_data, [])

            next_token = res.meta['next_token']
            running = next_token
            self._logger.info(f'Next token: {next_token}')
            await asyncio.sleep(1)
