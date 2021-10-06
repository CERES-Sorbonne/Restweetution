import io
from abc import ABC
from typing import List, Iterator
from restweetution.models.tweet import Tweet, Rule, User, StreamRule
from restweetution.storage.storage import Storage


class StorageWrapper(ABC):
    def __init__(self, storage: Storage):
        """
        Abstract Class that provides the template for every other storage wrapper
        :param storage: the storage to wrap
        """
        self.storage = storage

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        pass

    def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> List[Tweet]:
        pass

    def save_rules(self, rules: List[Rule]):
        pass

    def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        pass

    def save_users(self, users: List[User]):
        pass

    def save_media(self, media_key: str, buffer: io.BufferedIOBase) -> str:
        pass

    def get_media(self, media_key) -> io.BufferedIOBase:
        pass

    def has_free_space(self) -> bool:
        pass