import hashlib
import logging
from io import BytesIO
from typing import List, Iterator

import imagehash
from PIL import Image

from restweetution.models.config import StorageConfig, FileStorageConfig, SSHFileStorageConfig
from restweetution.models.tweet import Tweet, Rule, StreamRule
from restweetution.storage.object_storage.filestorage import FileStorage, SSHFileStorage
from restweetution.storage.object_storage.object_storage_wrapper import ObjectStorageWrapper
from restweetution.storage.storage_wrapper import StorageWrapper


class StorageManager:
    def __init__(self, tweets_storages: List[StorageConfig], media_storages:List[StorageConfig], partial_hash: bool = True):
        """
        Utility class to provide a single entry point to a Collector in order to perform all storages operations
        :param tweets_storages:
        :param media_storages:
        :param partial_hash:
        """
        self.tweets_storages = [self._resolve_storage(s) for s in tweets_storages]
        self.media_storages = [self._resolve_storage(s) for s in media_storages]
        self.partial_hash = partial_hash
        self.logger = logging.getLogger("Collector.Storage")

    def __str__(self):
        s = "    Tweets, Users and Rules stored at: \n                "
        for t in self.tweets_storages:
            s += "- " + str(t) + "\n                "
        s += "Pictures, Gif and Videos stored at: \n                "
        for m in self.media_storages:
            s += "- " + str(m)
        return s

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        # save collected tweet in every tag folder
        errors = 0
        for s in self.tweets_storages:
            if s.has_free_space:
                s.save_tweets(tweets, tags)
            else:
                errors += 1
                self.logger.warning(f"Maximum size reached for storage {str(s)}")
        if errors == len(self.tweets_storages):
            raise OSError("The maxsize of the storage directory has been reached")

    def get_tweets(self, tags: List[str] = None, ids: List[str] = None, duplicate: bool = False) -> Iterator[Tweet]:
        storages = [self.tweets_storages[0]] if not duplicate else self.tweets_storages
        for s in storages:
            for r in s.get_tweets(tags=tags, ids=ids):
                yield r

    def save_rules(self, rules: List[Rule]):
        """
       Persist a list of rules if not existing
       :param rules: list of rules
       :return: none
        """
        for s in self.tweets_storages:
            s.save_rules(rules)

    def get_rules(self, ids: List[str] = None, duplicate: bool = False) -> Iterator[StreamRule]:
        """
        Returns an iterator on the rules of the stream
        :param ids:
        :param duplicate:
        :return:
        """
        storages = [self.tweets_storages[0]] if not duplicate else self.tweets_storages
        for s in storages:
            for r in s.get_rules(ids):
                yield r

    def get_rules_ids(self) -> List[str]:
        return [r.id for r in self.get_rules()]

    def save_users(self):
        pass

    def save_media(self):
        pass

    def get_media(self):
        pass

    def _save_video(self):
        pass

    def _compute_signature(self, buffer: bytes):
        if self.partial_hash:
            img = Image.open(BytesIO(buffer))
            return str(imagehash.average_hash(img))
        else:
            return hashlib.sha1(buffer).hexdigest()

    @staticmethod
    def _resolve_storage(config: StorageConfig) -> StorageWrapper:
        """
        Utility method that takes a StorageConfig as input and returns a wrapped storage
        :param config: the storage config
        :return: a storage wrapper, which means a storage that exposes all methods to save or get data
        """
        if isinstance(config, FileStorageConfig):
            return ObjectStorageWrapper(FileStorage(config))
        elif isinstance(config, SSHFileStorageConfig):
            return ObjectStorageWrapper(SSHFileStorage(config))
        else:
            raise ValueError(f"Unhandled type of storage: {type(config)}")

