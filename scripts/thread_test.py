from __future__ import unicode_literals

import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Dict

import youtube_dl
from pydantic import BaseModel

from restweetution.utils import fire_and_forget


class VideoDownloadResult(BaseModel):
    error: Dict = None
    filename: str = None


class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    print(d)

    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def build_hook(res: VideoDownloadResult):
    def hook(d):
        if d['status'] == 'finished':
            if 'filename' in d:
                res.filename = d['filename']
        if 'error' in d:
            res.error = d['error']

    return hook


def download_video(url):
    res = VideoDownloadResult()
    ydl_opts = {
        'logger': MyLogger(),
        'progress_hooks': [build_hook(res)],
        # 'outtmpl': '/Users/david/Movies/%(extractor_key)s/%(extractor)s-%(id)s-%(title)s.%(ext)s',

    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            res.error = {'message': e.__str__()}

    return res


async def simulate():
    while True:
        print('lala')
        await asyncio.sleep(1)


async def main():
    url = 'https://twitter.com/Shanna_917/status/1615433017819815943'
    with ProcessPoolExecutor(max_workers=2) as pool:
        fire_and_forget(simulate())
        task = asyncio.get_event_loop().run_in_executor(pool, download_video, url)
        await task
        print(task.result())


if __name__ == '__main__':
    asyncio.run(main())
