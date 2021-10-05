from io import BytesIO
from typing import List

import imagehash
from PIL import Image

from restweetution.models.config import StorageConfig, FileStorageConfig, SSHFileStorageConfig
from restweetution.models.tweet import Tweet, Rule
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

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        # save collected tweet in every tag folder
        for s in self.tweets_storages:
            s.save_tweets(tweets, tags)

    def get_tweets(self):
        pass

    def save_rules(self, rules: List[Rule]):
        """
       Persist a list of rules if not existing
       :param rules: list of rules
       :return: none
        """
        for s in self.tweets_storages:
            s.save_rules(rules)

    def get_rules(self):
        pass

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
            pass

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