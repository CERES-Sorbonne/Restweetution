import asyncio
import logging
from typing import List, Dict, Optional

from restweetution.downloaders.media_downloader import MediaDownloader
from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter.media import Media
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.poll import Poll
from restweetution.models.rule import Rule
from restweetution.models.twitter.tweet import Tweet
from restweetution.models.twitter.user import User
from restweetution.storage_manager.storage_join import FirstFoundJoin
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage
from restweetution.storages.storage import Storage


class StorageManager:
    def __init__(self,
                 main_storage: PostgresStorage,
                 media_root_dir: str = None,
                 download_media: bool = False):
        """
        Utility class to provide a single entry point to a Collector in order to perform all storages operations
        """

        self._storages: List[Storage] = []
        self._storage_tags: Dict[str, List[str]] = {}

        self.main_storage = main_storage
        self.add_storage(storage=main_storage)

        self._download_media = download_media
        self._media_downloader: Optional[MediaDownloader] = None

        if media_root_dir:
            self.set_media_downloader(media_root_dir, download_media)

        self.logger = logging.getLogger("StorageManager")
        self._join_storage = FirstFoundJoin
        self.average_hash = False

    def __str__(self):
        s = "    Tweets, Users and Rules stored at: \n                "
        for t in self.get_storages():
            s += "- " + t.name + ': [' + t.__class__.__name__ + "] "
            if self._storage_tags[t.name]:
                s += "Tags: " + str(self._storage_tags[t.name])
            else:
                s += "All tags"
            s += "\n                "
        if self._media_downloader and self._download_media:
            s += f"Pictures, Gif and Videos stored at: {self._media_downloader.get_root()}\n"
        return s

    def set_media_downloader(self, media_root_dir: str, active: bool = True):
        self._media_downloader = MediaDownloader(root=media_root_dir, storage=self.main_storage, active=active)

    def get_media_downloader_active(self):
        return self._media_downloader.is_downloading()

    def get_media_downloader(self):
        return self._media_downloader

    # Storage functions
    def add_storage(self, storage: Storage, tags: List[str] = None):
        """
        Add Storage to the storage manager. In order to listen to specific tags a list of tags can be given
        :param storage: Storage
        :param tags: List of tags
        """
        if storage.name in [s.name for s in self._storages]:
            self.logger.warning(f'Storage name must be unique! name: {storage.name} is already taken')
            return
        self._storages.append(storage)
        self._storage_tags[storage.name] = []

        if tags:
            self.add_storage_tags(storage, tags)

    def remove_storages(self, names: List[str]):
        """
        Removes storages from the storage manager by storage names
        :param names: List of storage names to be removed
        """
        to_delete = [s.name for s in self._storages if s.name in names]
        for name in to_delete:
            self._storage_tags.pop(name)
        self._storages = [s for s in self._storages if s.name not in to_delete]

    def remove_all_storages(self):
        """
        Removes all storages from the storage manager
        """
        self._storages = []
        self._storage_tags = {}

    def add_storage_tags(self, storage: Storage, tags: List[str]):
        """
        Add tags to a storage
        :param storage: Storage
        :param tags: List of tags
        """
        name = storage.name
        for tag in [t for t in tags if t not in self._storage_tags[name]]:
            self._storage_tags[name].append(tag)

    def remove_storage_tags(self, storage: Storage, tags: List[str]):
        """
        Remove tags from storage
        :param storage: Storage
        :param tags: List of togs to be removed
        """
        name = storage.name
        if not self._storage_tags[name]:
            return
        self._storage_tags[name] = [s for s in self._storage_tags[name] if s not in tags]

    def remove_all_storage_tags(self, storage: Storage):
        """
        Remove all tags from a storage
        :param storage: Storage
        """
        self._storage_tags[storage.name] = []

    def set_storage_tags(self, storage: Storage, tags: List[str]):
        """
        Set tags for storage
        :param storage: Storage
        :param tags: List of togs to be set
        """
        self.remove_all_storage_tags(storage)
        self.add_storage_tags(storage, tags)

    def get_storages_listening_to_tags(self, tags: List[str] = None) -> List[Storage]:
        """
        Get list of storages that have at least one of the tags
        storages that have no tags set listen to all tags and are also returned
        :param tags: List of tags
        :return: List of Storage
        """
        if tags is None:
            tags = []

        storages = self._storages
        storages = [s for s in storages if self._has_tags(s, tags) or self._has_no_tags(s)]
        return storages

    def get_storages(self) -> List[Storage]:
        """
        Get storages connected to the storage manager
        :return: List of storages
        """
        return self._storages

    # Save functions
    def save_bulk(self, bulk_data: BulkData):
        """
        Save data in bulk
        :param bulk_data: BulkData object
        """
        tags = [r.tag for r in bulk_data.get_rules()]
        tasks = []
        storages = self.get_storages_listening_to_tags(tags)
        for s in storages:
            tasks.append(asyncio.create_task(s.save_bulk(bulk_data)))
        if self.main_storage not in storages and self._download_media and bulk_data.medias:
            tasks.append(asyncio.create_task(self.main_storage.save_medias(list(bulk_data.medias.values()))))
        return tasks

    def save_error(self, error):
        """
        Save a system error in storages that are registered as error_storage
        :param error: Error data
        """
        return asyncio.create_task(self.main_storage.save_error(error))

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        """
        Save tweets
        :param tweets: List of tweets
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_tweets(tweets)))
        return tasks

    def save_users(self, users: List[User], tags: List[str] = None):
        """
        Save users
        :param users: List of users
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_users(users)))
        return tasks

    def save_rules(self, rules: List[Rule], tags: List[str] = None):
        """
        Save rules
        :param rules: List of rules
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_rules(rules)))
        return tasks

    def save_polls(self, polls: List[Poll], tags: List[str] = None):
        """
        Save polls
        :param polls: List of polls
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_polls(polls)))
        return tasks

    def save_places(self, places: List[Place], tags: List[str] = None):
        """
        Save places
        :param places: List of places
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_places(places)))
        return tasks

    def save_media(self, medias: List[Media], tags: List[str] = None):
        """
        Take a media list, send them to the media downloader
        """
        tasks = []
        storages = self.get_storages_listening_to_tags(tags)
        for s in storages:
            tasks.append(asyncio.create_task(s.save_medias(medias)))
        if self.main_storage not in storages and self._download_media:
            tasks.append(asyncio.create_task(self.main_storage.save_medias(medias)))
        return tasks

    # Get functions
    async def get_error(self, **kwargs):
        """
        Get system errors from and only from the main storage
        """
        return await self.main_storage.get_errors(**kwargs)

    async def get_tweets(self, tags: List[str] = None, **kwargs):
        """
        Get tweets
        :param tags: List of tags
        """
        storages = self.get_storages_listening_to_tags(tags)
        return await self._join_storage.get_tweets(storages=storages, **kwargs)

    async def get_users(self, tags: List[str] = None, **kwargs):
        """
        Get users
        :param tags: List of tags
        """
        storages = self.get_storages_listening_to_tags(tags)
        return await self._join_storage.get_users(storages=storages, **kwargs)

    async def get_rules(self, tags: List[str] = None, **kwargs):
        """
        Get rules
        :param tags: List of tags
        """
        storages = self.get_storages_listening_to_tags(tags)
        return await self._join_storage.get_rules(storages=storages, **kwargs)

    async def get_polls(self, tags: List[str] = None, **kwargs):
        """
        Get polls
        :param tags: List of tags
        """
        storages = self.get_storages_listening_to_tags(tags)
        return await self._join_storage.get_polls(storages=storages, **kwargs)

    async def get_places(self, tags: List[str] = None, **kwargs):
        """
        Get places
        :param tags: List of tags
        """
        storages = self.get_storages_listening_to_tags(tags)
        return await self._join_storage.get_places(storages=storages, **kwargs)

    async def get_medias(self, tags: List[str] = None, **kwargs):
        """
        Get Medias
        """
        storages = [s for s in self.get_storages_listening_to_tags(tags) if s is not self.main_storage]
        storages = [self.main_storage, *storages]

        return await self._join_storage.get_medias(storages=storages, **kwargs)

    def get_status(self):
        return self._media_downloader.get_status()

    async def request_rules(self, rules: List[Rule]):
        return await self.main_storage.request_rules(rules)

    # private utils
    def _has_tags(self, storage: Storage, tags):
        """
        Tweet if the given storage has at least one of the tags
        """
        shared = [t for t in self._storage_tags[storage.name] if t in tags]
        return len(shared) > 0

    def _has_no_tags(self, storage: Storage):
        return self._storage_tags[storage.name] == []
