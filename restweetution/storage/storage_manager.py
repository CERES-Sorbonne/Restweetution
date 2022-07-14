import asyncio
import io
import logging
from io import BytesIO
from typing import List, Dict, Union

import imagehash
from PIL import Image

from restweetution.models.stream_rule import StreamRule
from restweetution.models.twitter.media import Media
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.poll import Poll
from restweetution.models.twitter.tweet import RestTweet
from restweetution.models.twitter.user import User
from restweetution.storage.document_storage import DocumentStorage
from restweetution.storage.object_storage.object_storage import FileStorage
from restweetution.utils import MediaDownloader


class StorageManager:
    def __init__(self):
        """
        Utility class to provide a single entry point to a Collector in order to perform all storages operations
        """

        self._doc_storages: List[DocumentStorage] = []
        self._media_storage: Union[FileStorage, None] = None
        self._doc_storage_tags: Dict[str, List[str]] = {}

        self.media_downloader = MediaDownloader(self.media_callback)
        self.logger = logging.getLogger("StorageManager")

        self.average_hash = False

    def __str__(self):
        s = "    Tweets, Users and Rules stored at: \n                "
        for t in self.get_document_storages():
            s += "- " + str(t) + "\n                "
        # s += "Pictures, Gif and Videos stored at: \n                "
        # for m in self.get_media_storages():
        #     s += "- " + str(m)
        return s

    def media_callback (self, media: Media, sha1: str, bytes_image: bytes = None, media_format: str = None):
        """
        Callback that will be passed to the media downloader to save the media once the download is finished
        """
        if bytes_image:
            await self._media_storage.save_media(f'{sha1}.{media_format}', io.BytesIO(bytes_image))
        await self._media_storage.save_media_link(media.media_key, sha1)
        # TODO: save more information in the document storage ?

    # Storage functions
    def add_doc_storage(self, storage: DocumentStorage, tags: List[str] = None):
        """
        Add DocumentStorage to the storage manager. In order to listen to specific tags a list of tags can be given
        :param storage: DocumentStorage
        :param tags: List of tags
        """
        if storage.name in [s.name for s in self._doc_storages]:
            self.logger.warning(f'Storage name must be unique! name: {storage.name} is already taken')
            return
        self._doc_storages.append(storage)
        self._doc_storage_tags[storage.name] = []

        if tags:
            self.add_doc_storage_tags(storage, tags)

    def set_media_storage(self, storage: FileStorage) -> None:
        self._media_storage = storage

    def remove_doc_storages(self, names: List[str]):
        """
        Removes document storages from the storage manager by storage names
        :param names: List of storage names to be removed
        """
        to_delete = [s.name for s in self._doc_storages if s.name in names]
        for name in to_delete:
            self._doc_storage_tags.pop(name)
        self._doc_storages = [s for s in self._doc_storages if s.name not in to_delete]

    def remove_all_doc_storages(self):
        """
        Removes all document storages from the storage manager
        """
        self._doc_storages = []
        self._doc_storage_tags = {}

    def add_doc_storage_tags(self, storage: DocumentStorage, tags: List[str]):
        """
        Add tags to a document storage
        :param storage: DocumentStorage
        :param tags: List of tags
        """
        name = storage.name
        for tag in [t for t in tags if t not in self._doc_storage_tags[name]]:
            self._doc_storage_tags[name].append(tag)

    def remove_doc_storage_tags(self, storage: DocumentStorage, tags: List[str]):
        """
        Remove tags from document storage
        :param storage: DocumentStorage
        :param tags: List of togs to be removed
        """
        name = storage.name
        if not self._doc_storage_tags[name]:
            return
        self._doc_storage_tags[name] = [s for s in self._doc_storage_tags[name] if s not in tags]

    def remove_all_doc_storage_tags(self, storage: DocumentStorage):
        """
        Remove all tags from a document storage
        :param storage: DocumentStorage
        """
        self._doc_storage_tags[storage.name] = []

    def set_doc_storage_tags(self, storage: DocumentStorage, tags: List[str]):
        """
        Set tags for document storage
        :param storage: DocumentStorage
        :param tags: List of togs to be set
        """
        self.remove_all_doc_storage_tags(storage)
        self.add_doc_storage_tags(storage, tags)

    def get_doc_storages_listening_to_tags(self, tags: List[str]) -> List[DocumentStorage]:
        """
        Get list of document storages that have at least one of the tags
        storages that have no tags set listen to all tags and are also returned
        :param tags: List of tags
        :return: List of DocumentStorage
        """
        storages = self._doc_storages
        storages = [s for s in storages if self._has_tags(s, tags) or self._has_no_tags(s)]
        return storages

    def get_document_storages(self) -> List[DocumentStorage]:
        """
        Get document storages connected to the storage manager
        :return: List of document storages
        """
        return self._doc_storages

    # saving functions
    def save_bulk(self, bulk_data, tags: List[str]):
        """
        Save data in bulk
        :param bulk_data: BulkData object
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_doc_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_bulk(bulk_data)))
        return tasks

    def save_error(self, error):
        """
        Save a system error in storages that are registered as error_storage
        :param error: Error data
        """
        tasks = []
        for s in [storage for storage in self._doc_storages if storage.is_error_storage]:
            tasks.append(asyncio.create_task(s.save_error(error)))
        return tasks

    def save_tweets(self, tweets: List[RestTweet], tags: List[str]):
        """
        Save tweets
        :param tweets: List of tweets
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_doc_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_tweets(tweets)))
        return tasks

    def save_users(self, users: List[User], tags: List[str]):
        """
        Save users
        :param users: List of users
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_doc_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_users(users)))
        return tasks

    def save_rules(self, rules: List[StreamRule], tags: List[str]):
        """
        Save rules
        :param rules: List of rules
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_doc_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_rules(rules)))
        return tasks

    def save_polls(self, polls: List[Poll], tags: List[str]):
        """
        Save polls
        :param polls: List of polls
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_doc_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_polls(polls)))
        return tasks

    def save_places(self, places: List[Place], tags: List[str]):
        """
        Save places
        :param places: List of places
        :param tags: List of tags
        """
        tasks = []
        for s in self.get_doc_storages_listening_to_tags(tags):
            tasks.append(asyncio.create_task(s.save_places(places)))
        return tasks

    # private utils
    def _has_tags(self, storage: DocumentStorage, tags):
        """
        Tweet if the given storage has at least one of the tags
        """
        shared = [t for t in self._doc_storage_tags[storage.name] if t in tags]
        return len(shared) > 0

    def _has_no_tags(self, storage: DocumentStorage):
        return self._doc_storage_tags[storage.name] == []

    # async def get_tweets(self, tags: List[str] = None, ids: List[str] = None, duplicate: bool = False) -> Iterator[
    #     TweetResponse]:
    #     storages = [self.tweets_storages[0]] if not duplicate else self.tweets_storages
    #     for s in storages:
    #         for r in await s.get_tweets(tags=tags, ids=ids):
    #             yield r

    async def save_media(self, media_list: List[Media]) -> None:
        """
        Take a media list, send them to the media downloader
        """
        for media in media_list:
            await self.media_downloader.download_media(media)



    @staticmethod
    def _computer_average_signature(buffer: bytes):
        img = Image.open(BytesIO(buffer))
        return str(imagehash.average_hash(img))
