import io
import json
import logging
import os
from abc import ABC
from typing import List, Union, Iterator

from restweetution.models.tweet import TweetResponse, User, StreamRule
from .filestorage_helper import FileStorageHelper
from .sshfilestorage_helper import SSHFileStorageHelper
from restweetution.storage.storage import Storage


class ObjectStorage(Storage, ABC):

    def __init__(self, storage_helper: Union[FileStorageHelper, SSHFileStorageHelper], tags: List[str] = None, max_size: int = None):
        """
        Generic Object Storage, like FileStorage or SSHFileStorage
        Provide a simple interface to manipulate tweets and media for all kind of Object Storages
        Note: all undocumented methods are documented in parent class
        :param storage_helper: a storage helper depending on the type of storage
        :param max_size: the maximum size available
        """
        super(ObjectStorage, self).__init__(tags=tags)
        self.storage = storage_helper
        self.logger = logging.getLogger("Collector.Storage.ObjectStorage")
        folders = ['tweets', 'rules', 'users', 'media_links']
        # aliases to access paths easily and avoid typo mistakes
        self.tweets, self.rules, self.users, self.media_links = [self._generate_sub_storages(x) for x in folders]

    def _generate_sub_storages(self, sub_path):
        """
        Utility function to create directories if they don't exist and
        return an alias to os.path.join with sub_path prefixed
        """
        self.storage.safe_create(sub_path)
        return lambda path=None: os.path.join(sub_path, path) if path else sub_path

    def __str__(self):
        return f"{type(self.storage).__name__} - {self.name}: {self.storage.root}"

    @property
    def has_free_space(self):
        return self.storage.has_free_space

    def save_tweets(self, tweets: List[TweetResponse], tags: List[str] = None):
        """
        :param tweets: a list of tweets to save
        :param tags: the list of tags of the rules that were triggered to collect this tweet
        """
        # TODO: make this concurrent
        for tweet in tweets:
            self.storage.put(tweet.json(exclude_none=True, ensure_ascii=False), self.tweets(f"{tweet.tweet.id}.json"))

    def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> Iterator[TweetResponse]:
        for f in self.storage.list(self.tweets()):
            yield TweetResponse.parse_file(self.tweets(f))

    def save_rules(self, rules: List[StreamRule]):
        for rule in rules:
            path = f"{rule.id}.json"
            if self.storage.exists(self.rules(path)):
                pass
            else:
                self.storage.put(rule.json(), self.rules(path))

    def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        files = self.storage.list(self.rules())
        if not files:
            return []
        if ids:
            # filter all files to fetch, keep only the ones with the ids specified in parameter
            files = [f for f in files if f.split('.')[0] in ids]
        for f in files:
            yield StreamRule(**json.load(self.storage.get(self.rules(f))))

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
        self.storage.put(signature, self.media_links(media_key))
        # then save the signature -> media_key link in a file to be able to count easily identical images
        self.save_signature_file(media_key, signature)
        # if we also have a average hash, save it the same way
        if average:
            self.save_signature_file(media_key, average)

    def save_signature_file(self, media_key, signature):
        if not self.storage.exists(self.media_links(signature)):
            self.storage.put(media_key, self.media_links(signature))
        else:
            content = self.storage.get(self.media_links(signature)).read().decode()
            content += "\n" + media_key
            self.storage.put(content, self.media_links(signature))


class FileStorage(ObjectStorage):
    def __init__(self, root: str, tags: List[str] = None, max_size: int = None):
        storage = FileStorageHelper(root=root, max_size=max_size)
        super(FileStorage, self).__init__(storage_helper=storage, tags=tags)


class SSHStorage(ObjectStorage):
    def __init__(self, root: str, tags: List[str] = None, max_size: int = None, *, host: str, user: str, password: str = ""):
        storage = SSHFileStorageHelper(root=root, max_size=max_size, host=host, user=user, password=password)
        super(SSHStorage, self).__init__(storage_helper=storage, tags=tags)
