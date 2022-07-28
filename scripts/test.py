import asyncio

import aiohttp
from tweepy.asynchronous import AsyncClient

from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter import TweetResponse
from restweetution.twitter_client import TwitterClient

token = 'AAAAAAAAAAAAAAAAAAAAAKYtawEAAAAALVyaGmcVIhSoWYp5vVY0ptgXg7E%3DJsZNkfHKm8kAZzy02bsJOJfjkXbfG8HWd2u4lLRaZLkT4qE2gk'

class Searcher(AsyncClient):
    async def search_loop_recent(self):
        bulk_data = BulkData()
        running = True
        while running:
            res = await self.search_recent_tweets(query="#cat", max_results=100)
            res_list = [TweetResponse(**r) for r in res]
            print(res_list)

    async def _parse_search_response(self):
        pass


async def launch():
    client = AsyncClient(bearer_token=token)
    res = await client.search_recent_tweets(query="#cat", max_results=100)
    print(res)
    # print(len(res.data))
    # print(res.meta)



asyncio.run(launch())
