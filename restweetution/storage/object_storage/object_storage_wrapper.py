import io
import json
import os
from typing import List, Union, Iterator
from copy import deepcopy

from restweetution.models.tweet import Tweet, User, StreamRule
from restweetution.storage.object_storage.filestorage import SSHFileStorage, FileStorage
from restweetution.storage.storage import Storage
from restweetution.storage.storage_wrapper import StorageWrapper


class ObjectStorageWrapper(StorageWrapper):
    def __init__(self, storage: Union[FileStorage, SSHFileStorage]):
        """
        Wrapper to Object Storages like FileStorage or SSHFileStorage
        Provide a simple interface to manipulate tweets and media for all kind of Object Storages
        Note: all undocumented methods are documented in parent class
        :param storage: the storage to wrap
        """
        super(ObjectStorageWrapper, self).__init__(storage)
        self.tweet_storage = self._generate_sub_storage('tweets')
        self.users_storage = self._generate_sub_storage('users')
        self.rules_storage = self._generate_sub_storage('rules')

    def __str__(self):
        return f"{type(self.storage).__name__} - {self.name}: {self.storage.root_directory}"

    @property
    def has_free_space(self):
        return self.storage.has_free_space

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        if not tags:
            tags = ["default"]
        for tweet in tweets:
            # save collected tweet in every tag folder
            for tag in tags:
                path = os.path.join(tag, f"{tweet.data.id}.json")
                self.tweet_storage.put(tweet.json(exclude_none=True, ensure_ascii=False), path)

    def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> Iterator[Tweet]:
        valid_tags = tags or self.tweet_storage.list()
        for t in valid_tags:
            for f in self.tweet_storage.list(t):
                yield Tweet(**json.load(self.tweet_storage.get(f)))

    def save_rules(self, rules: List[StreamRule]):
        for rule in rules:
            path = f"{rule.id}.json"
            if self.rules_storage.exists(path):
                pass
            else:
                self.rules_storage.put(rule.json(), path)

    def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        files = self.rules_storage.list()
        if not files:
            return []
        if ids:
            # filter all files to fetch, keep only the ones with the ids specified in parameter
            files = [f for f in files if f.split('.')[0] in ids]
        for f in files:
            yield StreamRule(**json.load(self.rules_storage.get(f)))

    def save_users(self, users: List[User]):
        pass

    def save_media(self, file_name: str, buffer: io.BufferedIOBase, signature: str) -> str:
        pass

    def get_media(self, media_key) -> io.BufferedIOBase:
        pass

    def _generate_sub_storage(self, sub_folder: str) -> Storage:
        """
        Create a clone of the storage with sub_folder as the root_directory
        Allow to manipulate easily different paths like 'rules', 'tweets', ...
        :param sub_folder: the name of the prefix that will be used in every operation
        :return: a Storage
        """
        storage = deepcopy(self.storage)
        storage.root_directory = os.path.join(storage.root_directory, sub_folder)
        return storage