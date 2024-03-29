import io
import json
import logging
import os
from abc import ABC
from typing import List, Iterator

from restweetution.models.twitter.tweet import TweetResponse, User, StreamAPIRule, Tweet
from .filestorage_helper import FileStorageHelper
from restweetution.storages.storage import Storage
from restweetution.models.bulk_data import BulkData


class ObjectStorage(Storage, ABC):

    def __init__(self, storage_helper: FileStorageHelper):
        """
        Generic Object Storage, like FileStorage or SSHFileStorage
        Provide a simple interface to manipulate tweets and media for all kind of Object Storages
        Note: all undocumented methods are documented in parent class
        :param storage_helper: a storage helper depending on the type of storage
        """
        # TODO: changer le tweet et media pour que ça soit géré par le storage manager
        self.storage_helper = storage_helper
        self.name = "FileStorage"
        super(ObjectStorage, self).__init__(name=str(self))
        self.logger = logging.getLogger("Collector.Storage.ObjectStorage")
        folders = ['tweets', 'rules', 'users', 'media_links']
        # aliases to access paths easily and avoid typo mistakes
        self.tweets, self.rules, self.users, self.media_links = [self._generate_sub_storages(x) for x in folders]

    def _generate_sub_storages(self, sub_path):
        """
        Utility function to create directories if they don't exist and
        return an alias to os.path.join with sub_path prefixed
        """
        self.storage_helper.safe_create(sub_path)
        return lambda path=None: os.path.join(sub_path, path) if path else sub_path

    def __str__(self):
        return f"{type(self.storage_helper).__name__} - {self.name}: {self.storage_helper.root}"

    @property
    def has_free_space(self):
        return self.storage_helper.has_free_space

    async def save_bulk(self, data: BulkData):
        await self.save_tweets(list(data.tweets.values()))
        # await self.save_users(list(data.users.values()))

    async def save_tweets(self, tweets: List[Tweet]):
        """
        :param tweets: a list of tweets to save
        :param tags: the list of tags of the rules that were triggered to collect this tweet
        """
        # TODO: make this concurrent
        for tweet in tweets:
            await self.storage_helper.put(tweet.json(exclude_none=True, ensure_ascii=False),
                                          self.tweets(f"{tweet.id}.json"))

    async def save_tweet(self, tweet: Tweet):
        await self.storage_helper.put(tweet.json(exclude_none=True, ensure_ascii=False),
                                      self.tweets(f"{tweet.id}.json"))

    def get_tweets(self, ids: List[str] = None, no_ids=None) -> Iterator[Tweet]:
        for f in self.storage_helper.list(self.tweets()):
            yield TweetResponse.parse_file(self.tweets(f))

    def save_rules(self, rules: List[StreamAPIRule]):
        for rule in rules:
            path = f"{rule.id}.json"
            if self.storage_helper.exists(self.rules(path)):
                pass
            else:
                self.storage_helper.put(rule.json(), self.rules(path))

    async def get_rules(self, ids: List[str] = None) -> Iterator[StreamAPIRule]:
        files = self.storage_helper.list(self.rules())
        if not files:
            yield []
        if ids:
            # filter all files to fetch, keep only the ones with the ids specified in parameter
            files = [f for f in files if f.split('.')[0] in ids]
        for f in files:
            yield StreamAPIRule(**json.load(await self.storage_helper.get(self.rules(f))))

    def save_users(self, users: List[User]):
        pass

    async def save_media(self, file_name: str, buffer: io.BufferedIOBase) -> str:
        return await self.storage_helper.put(buffer, file_name)

    def get_media(self, media_key) -> io.BufferedIOBase:
        pass

    def list_dir(self) -> List[str]:
        return self.storage_helper.list()

    def save_media_link(self, media_key, signature, average=None):
        """
        Save the links between a media key, and it's computed signature,
         and eventually an average signature to find similar images
        """
        # first save a media_key -> signature file to be able to quickly find the signature from the media_key
        self.storage_helper.put(signature, self.media_links(media_key))
        # then save the signature -> media_key link in a file to be able to count easily identical images
        self.save_signature_file(media_key, signature)
        # if we also have an average hash, save it the same way
        if average:
            self.save_signature_file(media_key, average)

    async def save_signature_file(self, media_key, signature):
        if not self.storage_helper.exists(self.media_links(signature)):
            await self.storage_helper.put(media_key, self.media_links(signature))
        else:
            sign = await self.storage_helper.get(self.media_links(signature))
            content = sign.read().decode()
            content += "\n" + media_key
            await self.storage_helper.put(content, self.media_links(signature))


class FileStorage(ObjectStorage):
    def __init__(self, root: str, max_size: int = None):
        storage = FileStorageHelper(root=root, max_size=max_size)
        super(FileStorage, self).__init__(storage_helper=storage)
