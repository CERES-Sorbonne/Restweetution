import io
import uuid
from abc import ABC
from typing import List, Iterator
from restweetution.models.tweet import TweetResponse, RuleRef, User, StreamRule
from restweetution.storage.storage_helper import StorageHelper


class Storage(ABC):
    def __init__(self, tags: List[str] = None):
        """
        Abstract Class that provides the template for every other storage
        :param tags: the list of tags that will be saved by this storage
        """
        self.tags_to_save = tags
        self.id = uuid.uuid4()

    @property
    def name(self):
        return f"{type(self).__name__}-{self.id}"

    def valid_tags(self, tags: List[str] = None):
        # if the storage was not tagged, then it accepts everything
        if not self.tags_to_save:
            return True
        # if the tweet matched a least one tag of the tags to save
        if tags and len(set(tags) - set(self.tags_to_save)) < len(set(tags)):
            return True
        return False

    def save_tweets(self, tweets: List[TweetResponse], tags: List[str] = None):
        pass

    def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> List[TweetResponse]:
        pass

    def save_rules(self, rules: List[RuleRef]):
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

    def save_media(self, file_name: str, buffer: io.BufferedIOBase) -> str:
        """
        Save a buffer to the storage and returns an uri to the stored file
        :param file_name: the signature of the media with the file_type
        :param buffer: the buffer to store
        :return: an uri to the resource created
        """
        pass

    def get_media(self, media_key) -> io.BufferedIOBase:
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