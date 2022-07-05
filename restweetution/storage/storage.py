import asyncio
import copy
import io
import time
from abc import ABC
from typing import List, Iterator, Optional, Callable

from restweetution.errors import handle_error
from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter.media import Media
from restweetution.models.twitter.tweet import TweetResponse, User, StreamRule, RestTweet


class Storage(ABC):
    def __init__(self, name: str = None, interval: int = 2, buffer_size: int = 100):
        """
        Abstract Class that provides the template for every other storage
        :param name: Give a name to identify this Storage Later
        :param interval: Clear storage every X seconds
        :param buffer_size: Max number of data the buffer can contain
        """
        self.name = name

        self._buffer_bulk_data: BulkData = BulkData()
        self._flush_interval = interval
        self._buffer_max_tweets = buffer_size

        self._last_buffer_flush: float = 0

        self._periodic_flush_task: Optional[asyncio.Task] = None

    def buffered_bulk_save(self, data: BulkData):
        """
        Save multiple type of data (bulk) at once
        """
        self._buffer_bulk_data += data

        if self._buffer_is_full():
            self._flush_buffer()

        self._start_periodic_flush_task()

    def _flush_buffer(self):
        """
        Save buffered data then clear the buffer
        """
        data = copy.deepcopy(self._buffer_bulk_data)
        self._clear_buffer()
        asyncio.create_task(self.bulk_save(data))
        self._last_buffer_flush = time.time()

    def _clear_buffer(self):
        self._buffer_bulk_data = BulkData()

    def _buffer_is_full(self):
        return len(self._buffer_bulk_data.tweets) > self._buffer_max_tweets

    def _start_periodic_flush_task(self):
        """
        Start the periodic flushing of the buffer
        """
        if self._periodic_flush_task:
            return
        # initialize
        self._last_buffer_flush = time.time()
        self._periodic_flush_task = asyncio.create_task(self._periodic_flush_loop())

    async def _periodic_flush_loop(self):
        """

        """
        while True:
            time_diff = time.time() - self._last_buffer_flush
            if time_diff >= self._flush_interval:
                self._flush_buffer()
                time_diff = 0

            await asyncio.sleep(self._flush_interval - time_diff)

    @handle_error
    async def bulk_save(self, data: BulkData):
        """
        Save the data to storage
        to be implemented in child class
        """
        pass

    async def save_tweet(self, tweet: RestTweet):
        await self.save_tweets([tweet])

    async def save_tweets(self, tweets: List[RestTweet]):
        bulk_data = BulkData()
        bulk_data.add_tweets(tweets)
        await self.bulk_save(bulk_data)

    async def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> List[TweetResponse]:
        pass

    async def save_rule(self, rule: StreamRule):
        pass

    async def save_rules(self, rules: List[StreamRule]):
        bulk_data = BulkData()
        bulk_data.add_rules(rules)
        await self.bulk_save(bulk_data)

    async def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        pass

    async def save_users(self, users: List[User]):
        bulk_data = BulkData()
        bulk_data.add_users(users)
        await self.bulk_save(bulk_data)

    async def get_users(self, ids: List[str] = None) -> Iterator[User]:
        pass

    async def save_media(self, media: List[Media]):
        bulk_data = BulkData()
        bulk_data.add_media(media)
        await self.bulk_save(bulk_data)

    async def get_media(self, media_key) -> io.BufferedIOBase:
        pass

    async def save_error(self, error: any):
        pass

    async def get_error(self):
        pass

    def list_dir(self) -> List[str]:
        pass

    def has_free_space(self) -> bool:
        pass

    async def save_media_link(self, media_key, signature, average_signature):
        """
        Save the match between the media_key and the computed signature of the media
        """
        pass
