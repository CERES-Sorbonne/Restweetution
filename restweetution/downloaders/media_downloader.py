import logging
from pathlib import Path
from typing import List, Callable

from pydantic import BaseModel

from restweetution.downloaders.download_queue import DownloadQueue
from restweetution.models.twitter.media import Media
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage
from restweetution.utils import AsyncEvent


class MediaDownloaderStatus(BaseModel):
    qsize_photo: int = None
    qsize_video: int = None
    qsize_gif: int = None


class MediaDownloader:

    def __init__(self, root: str, storage: PostgresJSONBStorage):
        """
        Utility class to queue the images download
        """
        root = Path(root)
        root_photo = root / 'photo'
        root_video = root / 'video'
        root_gif = root / 'gif'
        self._root = root.__str__()

        self._logger = logging.getLogger("MediaDownloader")

        self.event_downloaded = AsyncEvent()

        self._queue_photo = DownloadQueue(root=root_photo.__str__(), storage=storage)
        self._queue_video = DownloadQueue(root=root_video.__str__(), storage=storage)
        self._queue_gif = DownloadQueue(root=root_gif.__str__(), storage=storage)

    # Public functions

    def status(self):
        return MediaDownloaderStatus(qsize_photo=self._queue_photo.qsize(),
                                     qsize_video=self._queue_video.qsize(),
                                     qsize_gif=self._queue_gif.qsize())

    def download_medias(self, medias: List[Media], callback: Callable = None):
        """
        Default function to save medias with the download manager
        :param medias: List of Media to download
        :param callback: Optional Callback to be called on download complete
        """

        for m in medias:
            if m.type == 'photo':
                self._queue_photo.download([m], callback)
            if m.type == 'video':
                self._queue_video.download([m], callback)
            if m.type == 'animated_gif':
                self._queue_gif.download([m], callback)

    def get_root(self):
        return self._root
