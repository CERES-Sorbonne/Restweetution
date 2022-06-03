import asyncio
import copy
import io
import time
from abc import ABC
from typing import List, Iterator, Optional

from restweetution.models.bulk_data import BulkData
from restweetution.models.tweet import TweetResponse, User, StreamRule, RestTweet


class AsyncStorage(ABC):
    def __init__(self, name: str = None, tweet: bool = False, media: bool = False, tags: List[str] = None,
                 interval: int = 2, buffer_size: int = 100):
        """
        Abstract Class that provides the template for every other storage
        :param name: Give a name to identify this Storage Later
        :param tweet: Is this storage used to store tweets ?
        :param media: Is this storage used to store media ?
        :param tags: Store only the data gathered with the rules identified with these tags.
        :param interval: Clear storage every X seconds.
        :param buffer_size: Max number of data the buffer can contain.
        """
        self.name = name
        self.tags_to_save = tags
        self._is_tweet_storage = tweet
        self._is_media_storage = media

        self._buffer_bulk_data: BulkData = BulkData()
        self._flush_interval = interval
        self._buffer_max_tweets = buffer_size

        self._last_buffer_flush: float = 0

        self._periodic_flush_task: Optional[asyncio.Task] = None

        if not self._is_media_storage and not self._is_tweet_storage:
            raise Exception(f'Storage: {self.name} tweet and media cant both be False')

    def is_tweet_storage(self):
        return self._is_tweet_storage

    def is_media_storage(self):
        return self._is_media_storage

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
                print(f'Timout flush: {time.time()}')

            await asyncio.sleep(self._flush_interval - time_diff)

    async def bulk_save(self, data: BulkData):
        pass

    async def save_tweet(self, tweet: RestTweet):
        pass

    async def save_tweets(self, tweets: List[RestTweet]):
        pass

    async def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> List[TweetResponse]:
        pass

    async def save_rule(self, rule: StreamRule):
        pass

    async def save_rules(self, rules: List[StreamRule]):
        pass

    async def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        pass

    async def save_users(self, users: List[User]):
        pass

    async def get_users(self, ids:List[str] = None) -> Iterator[User]:
        pass

    async def save_media(self, file_name: str, buffer: io.BufferedIOBase) -> str:
        """
        Save a buffer to the storage and returns an uri to the stored file
        :param file_name: the signature of the media with the file_type
        :param buffer: the buffer to store
        :return: an uri to the resource created
        """
        pass

    async def get_media(self, media_key) -> io.BufferedIOBase:
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
