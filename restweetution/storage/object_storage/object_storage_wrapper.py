import io
import os
from typing import List, Union

from restweetution.models.tweet import Tweet, Rule, User
from restweetution.storage.object_storage.filestorage import SSHFileStorage, FileStorage
from restweetution.storage.storage_wrapper import StorageWrapper


class ObjectStorageWrapper(StorageWrapper):
    def __init__(self, storage: Union[FileStorage, SSHFileStorage]):
        """
        Wrapper to Object Storages like FileStorage or SSHFileStorage
        Provide a simple interface to manipulate tweets and media for all kind of Object Storages
        :param storage: the storage to wrap
        """
        super(ObjectStorageWrapper, self).__init__(storage)

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        if not tags:
            tags = [""]
        for tweet in tweets:
            # save collected tweet in every tag folder
            for tag in tags:
                path = os.path.join(tag, f"{tweet.data.id}.json")
                self.storage.put(tweet.json(exclude_none=True, ensure_ascii=False), path)

    def get_tweets(self, tag: str, ids: List[str] = None) -> List[Tweet]:
        pass

    def save_rules(self, rules: List[Rule]):
        """
        Persist a list of rules if not existing
        :param rules: list of rules
        :return: none
        """
        for rule in rules:
            path = os.path.join('rules', f"{rule.id}.json")
            if self.storage.exists(path):
                pass
            else:
                self.storage.put(rule.json(), path)

    def get_rules(self, ids: List[str] = None) -> List[Rule]:
        pass

    def save_users(self, users: List[User]):
        pass

    def save_media(self, media_key: str, buffer: io.BufferedIOBase) -> str:
        pass

    def get_media(self, media_key) -> io.BufferedIOBase:
        pass