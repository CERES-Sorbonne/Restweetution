import io
import uuid
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
        self.id = uuid.uuid4()

    @property
    def name(self):
        return f"{type(self.storage).__name__}-{self.id}"

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        pass

    def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> List[Tweet]:
        pass

    def save_rules(self, rules: List[Rule]):
        """
        Persist a list of rules if not existing
        :param rules: list of rules
        :return: none
        """
        pass

    def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        pass

    def save_users(self, users: List[User]):
        pass

    def save_media(self, file_name: str, buffer: io.BufferedIOBase, signature: str) -> str:
        """
        Save a buffer to the storage and returns an uri to the stored file
        :param file_name: the unique identifier to the media with the file_type
        :param buffer: the buffer to store
        :param signature: the hash of the file, used to find duplicate
        :return: an uri to the resource created
        """
        pass

    def get_media(self, media_key) -> io.BufferedIOBase:
        pass

    def list_media(self) -> List[str]:
        pass

    def has_free_space(self) -> bool:
        pass