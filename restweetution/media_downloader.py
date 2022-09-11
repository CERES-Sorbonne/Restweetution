import asyncio
import hashlib
import io
import logging
from typing import Dict, List

import aiohttp
from pydantic import BaseModel

from restweetution.models.event_data import EventData
from restweetution.models.twitter.media import Media
from restweetution.storages.object_storage.filestorage_helper import FileStorageHelper
from restweetution.storages.storage import Storage


class MediaCache(BaseModel):
    sha1: str
    format: str


class MediaDownloader:

    def __init__(self, root: str, storage: Storage, auto_download=True):
        """
        Utility class to queue the images download
        """
        self._logger = logging.getLogger("MediaDownloader")

        self._url_cache = {}
        self._media_key_cache: Dict[str, MediaCache] = {}

        self._storage = storage

        self._auto_download = None
        self.set_auto_download(auto_download)

        self._file_helper = FileStorageHelper(root)
        self._download_queue = asyncio.Queue()
        self._process_queue_task = None

    # Public functions

    async def save_medias(self, medias: List[Media]):
        """
        Default function to save medias with the download manager
        :param medias: List of Media to save
        """
        await self._storage.save_medias(medias)
        if not self._auto_download:
            for m in medias:
                self._add_download_task(m)

    def set_auto_download(self, value: bool):
        """
        Set automatic download of Medias that are added to the storage
        :param value: True or False
        """
        self._auto_download = value
        if self._auto_download:
            self._storage.save_event.add(self._medias_save_event_handler)
        elif self._medias_save_event_handler in self._storage.save_event:
            self._storage.save_event.remove(self._medias_save_event_handler)

    def get_root(self):
        return self._file_helper.root

    # Internal

    async def _medias_save_event_handler(self, event_data: EventData):
        medias = [m for m in event_data.data.get_medias() if m.media_key in event_data.added.medias]
        for m in medias:
            self._add_download_task(m)

    def _add_download_task(self, media: Media):
        """
        Add Media to the download queue
        """
        self._download_queue.put_nowait(media)
        if not self._process_queue_task:
            self._process_queue_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """
        Loop to empty the queue
        """
        await self._load_cache_from_storage()
        while True:
            media = await self._download_queue.get()
            await self._safe_download(media)

    async def _write_media(self, media: Media):
        """
        Write media to file storage
        :param media: Media
        """
        filename = media.sha1 + '.' + media.format
        await self._file_helper.put(key=filename, buffer=media.raw_data)
        self._logger.info(f' Downloaded image | sha1: {media.sha1}')

    async def _update_media_from_cache(self, media: Media):
        """
        Updates media value with the cached values
        """
        if media.media_key in self._media_key_cache:
            return True
        if media.url in self._url_cache:
            cache = self._url_cache[media.url]
            media.sha1 = cache.sha1
            media.format = cache.format
            self._cache_media(media)
            await self._storage.save_medias([media])
            return True
        return False

    def _cache_media(self, media):
        """
        Cache media
        """
        cache = MediaCache(sha1=media.sha1, format=media.format)
        self._media_key_cache[media.media_key] = cache
        self._url_cache[media.url] = cache

    async def _load_cache_from_storage(self):
        """
        Load Media cache from storage
        """
        medias = await self._storage.get_medias()
        for m in medias:
            if m.sha1 and m.url:
                self._cache_media(m)

    async def _safe_download(self, media: Media):
        """
        Checks if the url was already downloaded before starting the download
        If the media_key or url is already present in cache we use it to complete the data without download
        """
        if await self._update_media_from_cache(media):
            return
        await self._download_by_type(media)

    async def _download_by_type(self, media):
        """
        Download the media and compute its signature
        """
        async with aiohttp.ClientSession() as session:
            if media.type == 'photo' and media.url:
                media_format = media.url.split('.')[-1]
                try:
                    res = await session.get(media.url)

                    bytes_image: bytes = await res.content.read()
                    buffer = io.BytesIO(bytes_image)
                    media.sha1 = self._compute_signature(bytes_image)
                    media.format = media_format

                    updated = Media(media_key=media.media_key,
                                    sha1=media.sha1,
                                    format=media_format,
                                    raw_data=buffer)

                    await self._write_media(updated)
                    self._cache_media(media)
                    await self._storage.save_medias([updated])
                except aiohttp.ClientResponseError as e:
                    self._logger.warning(f"There was an error downloading image {media.url}: " + str(e))
                    # TODO: add an error handler here ?
                    return
            else:
                # TODO: use the video downloader
                pass

    @staticmethod
    def _compute_signature(buffer: bytes):
        return hashlib.sha1(buffer).hexdigest()
