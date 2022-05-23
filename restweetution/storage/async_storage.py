import io
from abc import ABC
from typing import List, Iterator
from restweetution.models.tweet import TweetResponse, User, StreamRule, RestTweet


class AsyncStorage(ABC):
    def __init__(self, name: str, tweet: bool = False, media: bool = False, tags: List[str] = None):
        """
        Abstract Class that provides the template for every other storage
        :param name: Give a name to identify this Storage Later
        """
        self.name = name
        self.tags_to_save = tags
        self._is_tweet_storage = tweet
        self._is_media_storage = media

        if not self._is_media_storage and not self._is_tweet_storage:
            raise Exception(f'Storage: {self.name} tweet and media cant both be False')

    def is_tweet_storage(self):
        return self._is_tweet_storage

    def is_media_storage(self):
        return self._is_media_storage

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

    def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        pass

    async def save_users(self, users: List[User]):
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

    def save_media_link(self, media_key, signature, average_signature):
        """
        Save the match between the media_key and the computed signature of the media
        """
        pass
