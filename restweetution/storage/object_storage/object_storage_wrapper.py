import io
import json
import logging
import os
from typing import List, Union, Iterator
from copy import deepcopy

from restweetution.models.tweet import Tweet, User, StreamRule
from restweetution.storage.object_storage.filestorage import SSHFileStorage, FileStorage
from restweetution.storage.storage import Storage
from restweetution.storage.storage_wrapper import StorageWrapper


class ObjectStorageWrapper(StorageWrapper):
    def __init__(self, storage: Union[FileStorage, SSHFileStorage], tags: List[str] = None, media: bool = False):
        """
        Wrapper to Object Storages like FileStorage or SSHFileStorage
        Provide a simple interface to manipulate tweets and media for all kind of Object Storages
        Note: all undocumented methods are documented in parent class
        :param storage: the storage to wrap
        :param media: will this be a media storage ? hack to avoid creating the substorages when its a media storage
        TODO: find a proper way to do that
        """
        super(ObjectStorageWrapper, self).__init__(storage, tags=tags)
        if not media:
            self.tweet_storage = self._generate_sub_storage('tweets')
            self.users_storage = self._generate_sub_storage('users')
            self.rules_storage = self._generate_sub_storage('rules')
            self.media_link_storage = self._generate_sub_storage('media_link_storage')

        self.logger = logging.getLogger("Collector.Storage.ObjectStorage")

    def __str__(self):
        return f"{type(self.storage).__name__} - {self.name}: {self.storage.root}"

    @property
    def has_free_space(self):
        return self.storage.has_free_space

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        """
        :param tweets: a list of tweets to save
        :param tags: the list of tags of the rules that were triggered to collect this tweet
        """
        # TODO: make this concurrent
        for tweet in tweets:
            self.tweet_storage.put(tweet.json(exclude_none=True, ensure_ascii=False), f"{tweet.data.id}.json")

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

    def save_media(self, file_name: str, buffer: io.BufferedIOBase) -> str:
        return self.storage.put(buffer, file_name)

    def get_media(self, media_key) -> io.BufferedIOBase:
        pass

    def list_dir(self) -> List[str]:
        return self.storage.list()

    def save_media_link(self, media_key, signature, average=None):
        """
        Save the links between a media key, and it's computed signature,
         and eventually an average signature to find similar images
        """
        # first save a media_key -> signature file to be able to quickly find the signature from the media_key
        self.media_link_storage.put(signature, media_key)
        # then save the signature -> media_key link in a file to be able to count easily identical images
        self.save_signature_file(media_key, signature)
        # if we also have a average hash, save it the same way
        if average:
            self.save_signature_file(media_key, average)

    def save_signature_file(self, media_key, signature):
        if not self.media_link_storage.exists(signature):
            self.media_link_storage.put(media_key, signature)
        else:
            content = self.media_link_storage.get(signature).read().decode()
            content += "\n" + media_key
            self.media_link_storage.put(content, signature)

    def _generate_sub_storage(self, sub_folder: str) -> Storage:
        """
        Create a clone of the storage with sub_folder as the root_directory
        Allow to manipulate easily different paths like 'rules', 'tweets', ...
        :param sub_folder: the name of the prefix that will be used in every operation
        :return: a Storage
        """
        storage = deepcopy(self.storage)
        storage.root = os.path.join(storage.root, sub_folder)
        return storage