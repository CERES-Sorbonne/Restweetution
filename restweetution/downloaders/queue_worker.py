import asyncio
import logging
import math
import traceback
from abc import ABC
from datetime import datetime
from typing import Any, Optional, Callable, Dict, List

from pydantic import BaseModel

logger = logging.getLogger('QueueDownloader')

SENTINEL = 'STOP'


class DownloadTask(BaseModel):
    url: str
    callback: Optional[Callable]


class DownloadResult(BaseModel):
    error: Dict = None
    filename: str = None
    sha1: str = None

    def format(self):
        return self.filename.split('.')[-1]


class DownloadState(BaseModel):
    start: datetime = datetime.now()
    current: int = 0
    total: int = -1
    speed: float = 0.0

    def progress(self):
        if self.total < 1:
            return 0
        return math.floor(self.current / self.total * 1000) / 10


class QueueDownloader(ABC):
    def __init__(self, root: str):
        self.root = root
        self._queue = asyncio.Queue()
        self._task: asyncio.Task | None = None

        self.actual_download: DownloadState | None = None
        self._past_results: List[DownloadResult] = []

    def is_downloading(self):
        return self.actual_download is not None

    def is_running(self):
        return self._task and not self._task.done()

    def qsize(self):
        return self._queue.qsize()

    async def _execute(self, url: str):
        raise NotImplementedError('Implement _execute(task) function')

    async def _process_queue(self):
        """
        Process Queue Loop
        Works through the queue one by one.
        @return:
        """
        while True:
            try:
                task: DownloadTask = await self._queue.get()
                # Stop if Sentinel is detected
                if task == SENTINEL:
                    return
                # Start a new download
                self.actual_download = DownloadState()
                res = await self._execute(task.url)
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

    def download(self, url: str, callback: Callable = None):
        task = DownloadTask(url=url, callback=callback)
        self._queue.put_nowait(task)
        if not self.is_running():
            self.start()
