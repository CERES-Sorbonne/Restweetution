import asyncio
import hashlib
import io
import logging
import traceback
from asyncio import Task
from typing import List, Optional, Callable

import aiohttp
from pydantic import BaseModel

from restweetution.models.config.downloaded_media import DownloadedMedia
from restweetution.models.twitter.media import Media
from restweetution.storages.object_storage.filestorage_helper import FileStorageHelper
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage
from restweetution.utils import Event


class MediaCache(BaseModel):
    sha1: str
    format: str


class DownloadTask(BaseModel):
    media: Media
    callback: Optional[Callable]


class MediaDownloader:

    def __init__(self, root: str, storage: PostgresJSONBStorage):
        """
        Utility class to queue the images download
        """
        self._logger = logging.getLogger("MediaDownloader")
        self._storage = storage

        self._file_helper = FileStorageHelper(root)
        self._download_queue = asyncio.Queue()
        self._process_queue_task: Optional[Task] = None

        self.event_downloaded = Event()

    # Public functions

    def get_root_dir(self):
        return self._file_helper.root

    def is_running(self):
        return self._process_queue_task and not self._process_queue_task.done()

    def download_medias(self, medias: List[Media], callback: Callable = None):
        """
        Default function to save medias with the download manager
        :param medias: List of Media to download
        :param callback: Optional Callback to be called on download complete
        """
        for m in medias:
            d_task = DownloadTask(media=m, callback=callback)
            self._add_download_task(d_task)

    def get_root(self):
        return self._file_helper.root

    def get_queue_size(self):
        return self._download_queue.qsize()

    def get_status(self):
        return {
            'queue_size': self.get_queue_size()
        }

    # Internal

    def _add_download_task(self, d_task: DownloadTask):
        """
        Add Media to the download queue
        """
        self._download_queue.put_nowait(d_task)
        if not self.is_running():
            self._process_queue_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """
        Loop to empty the queue
        """
        while True:
            try:
                d_task: DownloadTask = await self._download_queue.get()
                media = d_task.media

                d_media = await self._find_same_media(media)
                if d_media:
                    await self._save_duplicate(media, d_media)
                    asyncio.create_task(d_task.callback(d_media))
                else:
                    res = await self._download_by_type(media)
                    if res and d_task.callback:
                        asyncio.create_task(d_task.callback(res))

            except Exception as e:
                self._logger.error(traceback.print_exc(limit=3))
                self._logger.error('Error inside _process_queue function : ' + e.__str__())

    async def _save_duplicate(self, media: Media, d_media: DownloadedMedia):
        to_save = DownloadedMedia(**media.dict(), sha1=d_media.sha1, format=d_media.format)
        await self._storage.save_downloaded_medias([to_save])

    async def _write_media(self, media: DownloadedMedia):
        """
        Write media to file storage
        :param media: Media
        """
        filename = media.sha1 + '.' + media.format
        await self._file_helper.put(key=filename, buffer=media.bytes_)
        self._logger.info(f' Downloaded image | sha1: {media.sha1}')

    async def _find_same_media(self, media: Media):
        """
        Checks if the url was already downloaded before starting the download
        If the media_key or url is already present in DB we return it
        """
        # find downloaded media with same media key or same url
        d_media = await self._storage.get_downloaded_medias(
            media_keys=[media.media_key],
            urls=[media.url],
            is_and=False
        )
        if d_media:
            return d_media[0]
        return None

    async def _download_by_type(self, media):
        """
        Download the media and compute its signature
        """
        if media.type == 'photo' and media.url:
            return await self._download_photo(media)

    async def _download_photo(self, media: Media):
        async with aiohttp.ClientSession() as session:
            media_format = media.url.split('.')[-1]
            try:
                res = await session.get(media.url)

                bytes_image: bytes = await res.content.read()
                buffer = io.BytesIO(bytes_image)
                sha1 = self._compute_signature(bytes_image)
                format_ = media_format

                downloaded = DownloadedMedia(**media.dict(), sha1=sha1, format=format_, bytes_=buffer)

                await self._write_media(downloaded)
                await self._storage.save_downloaded_medias([downloaded])
                return downloaded
            except aiohttp.ClientResponseError as e:
                self._logger.warning(f"There was an error downloading image {media.url}: " + str(e))
                # TODO: add an error handler here ?
                return

    @staticmethod
    def _compute_signature(buffer: bytes):
        return hashlib.sha1(buffer).hexdigest()
