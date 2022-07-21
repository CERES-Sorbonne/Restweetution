import asyncio
import hashlib
import io
import logging
from typing import Dict

import aiohttp
from pydantic import BaseModel

from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter.media import Media
from restweetution.storage.document_storages.document_storage import Storage
from restweetution.storage.document_storages.object_storage.filestorage_helper import FileStorageHelper


class MediaCache(BaseModel):
    sha1: str
    format: str


class MediaDownloader:

    def __init__(self, root: str, storage: Storage, listen=False):
        """
        Utility class to queue the images download
        """
        self._logger = logging.getLogger("MediaDownloader")

        self._url_cache = {}
        self._media_key_cache: Dict[str, MediaCache] = {}

        self._storage = storage
        if listen:
            self._storage.listen_save_event(self._download_medias_from_event)

        self._file_helper = FileStorageHelper(root)
        self._download_queue = asyncio.Queue()
        self._process_queue_task = None

    def get_root(self):
        return self._file_helper.root

    def download_media(self, media: Media):
        """
        Main method that just adds a media to the download queue
        """
        self._download_queue.put_nowait(media)
        if not self._process_queue_task:
            asyncio.create_task(self._process_queue())

    async def _download_medias_from_event(self, data: BulkData):
        medias = list(data.medias.values())
        for m in medias:
            self.download_media(m)

    async def _process_queue(self):
        """
        Loop to empty the queue
        """
        await self._load_cache()
        while True:
            media = await self._download_queue.get()
            await self._download(media)

    async def _write_media(self, media: Media):
        filename = media.sha1 + '.' + media.format
        await self._file_helper.put(key=filename, buffer=media.raw_data)
        self._cache_media(media)
        self._logger.info(f' Downloaded image | sha1: {media.sha1}')

    async def _download(self, media: Media):
        """
        Check if the url was already downloaded
        """
        if await self._update_media_from_cache(media):
            print('already downloaded')
            return
        await self._download_by_type(media)

    async def _update_media_from_cache(self, media: Media):
        if media.media_key in self._media_key_cache:
            return True
        if media.url in self._url_cache:
            cache = self._url_cache[media.url]
            media.sha1 = cache.sha1
            media.format = cache.format
            await self._storage.update_medias([media])
            return True
        return False

    def _cache_media(self, media):
        cache = MediaCache(sha1=media.sha1, format=media.format)
        self._media_key_cache[media.media_key] = cache
        self._url_cache[media.url] = cache

    async def _load_cache(self):
        medias = await self._storage.get_medias()
        for m in medias:
            if m.sha1:
                self._cache_media(m)

    async def _download_by_type(self, media):
        """
        Download the media and compute its signature
        """
        async with aiohttp.ClientSession() as session:
            if media.type == 'photo':
                media_format = media.url.split('.')[-1]
                try:
                    res = await session.get(media.url)
                    bytes_image: bytes = await res.content.read()
                    buffer = io.BytesIO(bytes_image)
                    sha1 = self._compute_signature(bytes_image)
                    # self.download_callback(media, sha1, bytes_image, media_format)
                    updated = Media(media_key=media.media_key,
                                    sha1=sha1,
                                    format=media_format,
                                    raw_data=buffer)

                    await self._write_media(updated)
                    await self._storage.update_medias([updated])
                except aiohttp.ClientResponseError as e:
                    self._logger.warning(f"There was an error downloading image {media.url}: " + str(e))
                    # TODO: add an error handler here ?
                    return
            else:
                # TODO: use the video downloader
                pass

    @staticmethod
    def _get_file_type(file_type: str) -> str:
        if file_type == "video":
            return "mp4"
        elif file_type == "photo":
            return "jpeg"
        else:
            # store gif files as mp4 because it's the way there are downloaded
            return "gif"

    @staticmethod
    def _compute_signature(buffer: bytes):
        return hashlib.sha1(buffer).hexdigest()
