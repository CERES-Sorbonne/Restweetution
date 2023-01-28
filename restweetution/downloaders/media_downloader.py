import asyncio
import logging
import traceback
from asyncio import Task
from typing import List, Optional, Callable

from pydantic import BaseModel

from restweetution.downloaders.photo_downloader import PhotoDownloader
from restweetution.downloaders.queue_worker import DownloadResult
from restweetution.downloaders.video_downloader import VideoDownloader
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.twitter.media import Media
from restweetution.storages.object_storage.filestorage_helper import FileStorageHelper
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage
from restweetution.utils import AsyncEvent


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

        self.event_downloaded = AsyncEvent()

        self._photo_downloader = PhotoDownloader(root=root)
        self._video_downloader = VideoDownloader(root=root)

    # Public functions

    def status(self):
        print(f'to dispatch: {self._download_queue.qsize()}')
        print(f'videos: {self._video_downloader.qsize()}')
        print(f'photos: {self._photo_downloader.qsize()}')
        print('\n')

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

    def _downloader_callback(self, d_task: DownloadTask):
        async def save_to_storage(res: DownloadResult):
            if not res.error:
                downloaded = DownloadedMedia(media_key=d_task.media.media_key, sha1=res.sha1, format=res.format())
                await self._storage.save_downloaded_medias([downloaded])
                self._logger.info(f'Downloaded {d_task.media.type} | sha1: {downloaded.sha1}')

                if d_task.callback:
                    asyncio.create_task(d_task.callback(downloaded))

        return save_to_storage

    async def _process_queue(self):
        """
        Loop to empty the queue
        """
        while True:
            try:
                # self.status()
                d_task: DownloadTask = await self._download_queue.get()
                media = d_task.media

                d_media = await self._find_same_media(media)
                if d_media:
                    await self._save_duplicate(media, d_media)
                    asyncio.create_task(d_task.callback(d_media))
                else:
                    self._download_by_type(media, self._downloader_callback(d_task))

            except Exception as e:
                self._logger.error(traceback.print_exc(limit=3))
                self._logger.error('Error inside _process_queue function : ' + e.__str__())

    async def _save_duplicate(self, media: Media, d_media: DownloadedMedia):
        """
        Save a media with same url as an already downloaded Media
        @param media: media
        @param d_media: already downloaded media
        @return:
        """
        to_save = DownloadedMedia(**media.dict(), sha1=d_media.sha1, format=d_media.format)
        await self._storage.save_downloaded_medias([to_save])

    async def _find_same_media(self, media: Media):
        """
        Checks if the url was already downloaded before starting the download
        If the media_key or url is already present in DB we return it
        """
        # find downloaded media with same media key or same url
        d_media = await self._storage.get_downloaded_medias(media_keys=[media.media_key], urls=[media.url],
                                                            is_and=False)
        if d_media:
            return d_media[0]
        return None

    def _download_by_type(self, media, callback: Callable):
        """
        Download the media according to type
        """
        if media.type == 'photo' and media.url:
            self._photo_downloader.download(media.url, callback)
        if media.type == 'video' and media.url:
            self._video_downloader.download(media.url, callback)
