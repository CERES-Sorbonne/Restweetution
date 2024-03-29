import asyncio
import copy
import time
from abc import ABC
from typing import List, Optional

from restweetution.errors import handle_error, FunctionNotImplementedError
from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.error import ErrorModel
from restweetution.models.rule import Rule
from restweetution.models.twitter.media import Media
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.poll import Poll
from restweetution.models.twitter.tweet import User, Tweet
from restweetution.storages.exporter.exporter import Exporter
from restweetution.utils import AsyncEvent, fire_and_forget


class Storage(Exporter, ABC):
    def __init__(self, name: str = None, interval: int = 0, buffer_size: int = 0, **kwargs):
        """
        Abstract Class that provides the template for every other storage
        By default all savings functions are implemented by using the save_bulk function
        A Storage can buffer the input if a saving interval and buffer size is given by calling buffered_bulk_save
        :param name: Give a name to identify this Storage Later, must be unique
        :param interval: Optional. Clear storage every X seconds
        :param buffer_size: Optional. Max number of data the buffer can contain
        """
        super().__init__(name)

        self._buffer_bulk_data: BulkData = BulkData()
        self._flush_interval = interval
        self._buffer_max_tweets = buffer_size

        self._last_buffer_flush: float = 0

        self._periodic_flush_task: Optional[asyncio.Task] = None

        self.save_event = AsyncEvent()
        self.update_event = AsyncEvent()

    # Configuration
    def get_config(self):
        pass

    # Events

    async def _emit_save_event(self, **kwargs):
        data = BulkData()
        if kwargs.get('bulk_data'):
            data = kwargs.get('bulk_data')
        if kwargs.get('tweets'):
            data.add_tweets(kwargs.get('tweets'))
        if kwargs.get('users'):
            data.add_users(kwargs.get('users'))
        if kwargs.get('rules'):
            data.add_rules(kwargs.get('rules'))
        if kwargs.get('polls'):
            data.add_polls(kwargs.get('polls'))
        if kwargs.get('places'):
            data.add_places(kwargs.get('places'))
        if kwargs.get('medias'):
            data.add_medias(kwargs.get('medias'))
        await self.save_event(data)

    # Save

    def buffered_bulk_save(self, data: BulkData):
        """
        Save multiple type of data (bulk) at once
        """
        self._buffer_bulk_data += data

        if self._buffer_is_full():
            self._flush_buffer()

        self._start_periodic_flush_task()

    @handle_error
    async def save_bulk(self, data: BulkData):
        """
        Save the data to storage
        to be implemented in child class
        """
        pass
    
    async def request_rules(self, rules: List[Rule]):
        pass

    async def save_tweet(self, tweet: Tweet):
        """
        Save tweet
        :param tweet: tweet
        """
        await self.save_tweets([tweet])

    async def save_tweets(self, tweets: List[Tweet]):
        """
        Save multiple tweets
        :param tweets: tweets
        """
        bulk_data = BulkData()
        bulk_data.add_tweets(tweets)
        await self.save_bulk(bulk_data)

    async def save_rule(self, rule: Rule):
        """
        Save rule
        :param rule: rule
        """
        await self.save_rules([rule])

    async def save_rules(self, rules: List[Rule]):
        """
        Save multiple rules
        :param rules: rules
        """
        bulk_data = BulkData()
        bulk_data.add_rules(rules)
        await self.save_bulk(bulk_data)

    async def save_user(self, user: User):
        """
        Save user
        :param user: user
        """
        await self.save_users([user])

    async def save_users(self, users: List[User]):
        """
        Save multiple users
        :param users: users
        """
        bulk_data = BulkData()
        bulk_data.add_users(users)
        await self.save_bulk(bulk_data)

    async def save_media(self, media: Media):
        """
        Save media
        :param media: medias
        """
        await self.save_medias([media])

    async def save_medias(self, medias: List[Media]):
        """
        Save multiple medias
        :param medias: medias
        """
        bulk_data = BulkData()
        bulk_data.add_medias(medias)
        await self.save_bulk(bulk_data)

    async def save_place(self, place: Place):
        """
        Save place
        :param place: place
        """
        await self.save_places([place])

    async def save_places(self, places: List[Place]):
        """
        Save multiple places
        :param places: places
        """
        bulk_data = BulkData()
        bulk_data.add_places(places)
        await self.save_bulk(bulk_data)

    async def save_poll(self, poll: Poll):
        """
        Save one poll
        :param poll: poll
        """
        await self.save_polls([poll])

    async def save_polls(self, polls: List[Poll]):
        """
        Save multiple polls
        :param polls: polls
        """
        bulk_data = BulkData()
        bulk_data.add_polls(polls)
        await self.save_bulk(bulk_data)

    async def save_error(self, error: ErrorModel):
        """
        Save RESTweetutionError. This function doesn't use bulk_data and should be used locally to avoid
        saving fails
        :param error: RESTweetutionError object
        """
        raise FunctionNotImplementedError('Save Error function not implemented')

    # buffer utils

    def _flush_buffer(self):
        """
        Save buffered data then clear the buffer
        """
        data = copy.deepcopy(self._buffer_bulk_data)
        self._clear_buffer()
        fire_and_forget(self.save_bulk(data))
        self._last_buffer_flush = time.time()

    def _clear_buffer(self):
        """
        clear buffer
        """
        self._buffer_bulk_data = BulkData()

    def _buffer_is_full(self):
        """
        :return: True if buffer is full
        """
        return len(self._buffer_bulk_data.tweets) > self._buffer_max_tweets

    def _start_periodic_flush_task(self):
        """
        Start the periodic flushing of the buffer if it's not running
        """
        if self._periodic_flush_task:
            return
        # initialize
        self._last_buffer_flush = time.time()
        self._periodic_flush_task = asyncio.create_task(self._periodic_flush_loop())

    async def _periodic_flush_loop(self):
        """
        utility loop for periodic saving of the buffered data
        """
        while True:
            time_diff = time.time() - self._last_buffer_flush
            if time_diff >= self._flush_interval:
                self._flush_buffer()
                time_diff = 0

            await asyncio.sleep(self._flush_interval - time_diff)

    # get functions
    async def get_users(self, **kwargs) -> List[User]:
        pass

    async def get_tweets(self, **kwargs) -> List[Tweet]:
        pass

    async def get_rules(self, **kwargs) -> List[Rule]:
        pass

    async def get_polls(self, **kwargs) -> List[Poll]:
        pass

    async def get_places(self, **kwargs) -> List[Place]:
        pass

    async def get_medias(self, **kwargs) -> List[Media]:
        pass

    async def get_errors(self, **kwargs) -> List[ErrorModel]:
        pass

    async def get_custom_datas(self, key: str) -> List[CustomData]:
        raise NotImplementedError('get_custom_datas function is not implemented')

    async def del_custom_datas(self, key: str):
        raise NotImplementedError('del_custom_datas function is not implemented')
