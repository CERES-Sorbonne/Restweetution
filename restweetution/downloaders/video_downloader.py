import asyncio
import datetime
import math
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import process
from typing import Dict, Coroutine, Callable, List

import youtube_dl
from pydantic import BaseModel

from restweetution.downloaders.queue_worker import QueueDownloader, DownloadResult, DownloadState
from restweetution.downloaders.utils import compute_signature_from_file


class MyLogger:
    @staticmethod
    def debug(msg):
        # print(msg)
        pass

    @staticmethod
    def warning(msg):
        # print(msg)
        pass

    @staticmethod
    def error(msg):
        print(msg)


def build_hook(res: DownloadResult, state: DownloadState):
    def hook(d):
        # print(d)
        if d['status'] == 'finished':
            if 'filename' in d:
                res.filename = d['filename']
        if 'error' in d:
            res.error = d['error']
        if d['status'] == 'downloading':
            state.current = d['total_bytes']
            state.total = d['total_bytes']
            state.speed = d['speed']

    return hook


class VideoDownloader(QueueDownloader):
    async def _execute(self, url: str):
        # print(self.actual_download)
        task = asyncio.get_event_loop().run_in_executor(None, self.sync_download_video, url,
                                                        self.actual_download)
        await task
        res: DownloadResult = task.result()
        res.sha1 = await compute_signature_from_file(res.filename)
        return res

    def sync_download_video(self, url, state: DownloadState):
        res = DownloadResult()
        ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [build_hook(res, state)],
            'outtmpl': self.root + '/video/%(extractor)s-%(id)s.%(ext)s',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                res.error = {'message': e.__str__()}
        return res
