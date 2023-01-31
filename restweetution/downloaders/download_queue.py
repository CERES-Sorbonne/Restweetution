import asyncio
import logging
import traceback
from abc import ABC
from typing import Optional, Callable, Dict, List

from aiopath import Path
from pydantic import BaseModel

from restweetution.downloaders.url_downloader import UrlDownloader
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.twitter import Media
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage

logger = logging.getLogger('DownloadQueue')

SENTINEL = 'STOP'


class DownloadTask(BaseModel):
    media: Media
    callback: Optional[Callable]


class DownloadQueueStatus(BaseModel):
    qsize: int
    current_url: str
    bytes_downloaded: int
    bytes_total: int
    progress_percentage: int


class DownloadQueue(ABC):
    def __init__(self, root: str, storage: PostgresJSONBStorage):
        self.root = Path(root)
        self._storage = storage
        self._queue = asyncio.Queue()
        self._task: asyncio.Task | None = None
        self._actual_media: Media | None = None
        self._downloader = UrlDownloader()

    def status(self):
        bytes_d, bytes_t = self._downloader.get_progress()
        url = self._downloader.get_url()
        percentage = self._downloader.get_progress_percentage()
        return DownloadQueueStatus(qsize=self.qsize(), current_url=url, bytes_downloaded=bytes_d, bytes_total=bytes_t,
                                   progress_percentage=percentage)

    def is_running(self):
        return self._task and not self._task.done()

    def qsize(self):
        return self._queue.qsize()

    def get_current_url(self):
        if self._actual_media is None:
            return None
        return self._actual_media.get_url()

    async def wait_finish(self):
        if self._task:
            await self._task
        return

    async def _download_media(self, media: Media):
        d_media = await self._find_same_media(media)
        if d_media:
            await self._save_duplicate(media, d_media)
            return

        res = await self._downloader.download_save_sha1(src_url=media.get_url(), dest_folder=self.root)
        d_media = DownloadedMedia(media_key=media.media_key, format=res.ext, sha1=res.sha1, media=media)
        await self._storage.save_downloaded_medias([d_media])

        logger.info(f'Downloaded {media.type} | sha1: {d_media.sha1}')

        return d_media

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

    async def _process_queue(self):
        """
        Process Queue Loop
        Works through the queue one by one.
        @return:
        """
        await self.root.mkdir(parents=True, exist_ok=True)
        while True:
            try:
                # if nothing to do, end process
                if self._queue.qsize() == 0:
                    return
                task: DownloadTask = await self._queue.get()
                # Stop if Sentinel is detected
                if task == SENTINEL:
                    return
                # Start a new download
                self._actual_media = task.media
                res = await self._download_media(task.media)
                # trigger callback
                if task.callback:
                    asyncio.create_task(task.callback(res))
                # end downloading state
                self.actual_download = None
            except Exception as e:
                # end downloading state
                self.actual_download = None
                logger.error(traceback.print_exc(limit=3))
                logger.error('Error inside _process_queue function : ' + e.__str__())

    def start(self):
        self._task = asyncio.create_task(self._process_queue())

    def download(self, medias: List[Media], callback: Callable = None):
        """
        Default function to save medias with the download manager
        :param medias: List of Media to download
        :param callback: Optional Callback to be called on download complete
        """
        for m in medias:
            d_task = DownloadTask(media=m, callback=callback)
            self._queue.put_nowait(d_task)

        if not self.is_running():
            self.start()
