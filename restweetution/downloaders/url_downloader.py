import hashlib
import math
import time

import aiofiles
import aiohttp
from aiopath import Path
from pydantic import BaseModel


class DownloadResult(BaseModel):
    filename: str
    ext: str
    sha1: str | None = None


class UrlDownloader:
    def __init__(self):
        self._is_downloading = False
        self._bytes_total = -1
        self._bytes_downloaded = 0
        self._current_url: str = ''

    def _init_download(self, url: str):
        self._is_downloading = True
        self._current_url = url
        self._bytes_downloaded = 0
        self._bytes_total = -1

    def _stop_download(self):
        self._is_downloading = False

    def get_progress_percentage(self):
        if self._bytes_total < 1:
            return 0
        return math.floor(self._bytes_downloaded / self._bytes_total * 1000) / 10

    def get_progress(self):
        return self._bytes_downloaded, self._bytes_total

    def get_url(self):
        return self._current_url

    def print_progress(self):
        print(f'[{self.get_progress_percentage()}%] {self._bytes_downloaded} / {self._bytes_total} bytes')

    def is_downloading(self):
        return self._is_downloading

    def _set_total(self, total: None | int | str):
        if total is None:
            self._bytes_total = -1
        else:
            self._bytes_total = int(total)

    async def download(self, src_url):
        try:
            connector = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(src_url) as resp:
                    self._init_download(src_url)
                    self._set_total(resp.headers.get("Content-Length"))
                    data = await resp.content.read()
                    self._bytes_downloaded = self._bytes_total
                    self._stop_download()
                    return data
        except Exception as e:
            self._stop_download()
            raise e

    async def download_stream(self, src_url, chunk_size=65536):
        try:
            connector = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(src_url) as resp:
                    self._init_download(src_url)
                    self._set_total(resp.headers.get("Content-Length"))
                    async for chunk in resp.content.iter_chunked(chunk_size):
                        self._bytes_downloaded += len(chunk)
                        yield chunk
            self._stop_download()
        except Exception as e:
            self._stop_download()
            raise e

    async def download_save(self, src_url, dest_file):
        async with aiofiles.open(dest_file, 'wb') as fd:
            data = await self.download(src_url)
            await fd.write(data)
            return data

    async def download_save_stream(self, src_url, dest_file, chunk_size=65536):
        async with aiofiles.open(dest_file, 'wb') as fd:
            async for chunk in self.download_stream(src_url, chunk_size=chunk_size):
                await fd.write(chunk)
                yield chunk

    async def download_save_sha1(self, src_url: str, dest_folder: str, ext: str = None, tmp_name: str = None):
        # use a tmp name with help of the url
        if tmp_name is None:
            tmp_name = time.time().__str__() + '-' + src_url.split('/')[-1]
        if ext is None:
            if tmp_name.find('.'):
                clean = tmp_name.rsplit('?', 1)[0]
                ext = clean.split('.')[-1]
            else:
                ext = 'unknown'

        filename = tmp_name + '.part'
        dest_file = Path(dest_folder) / filename

        sha1 = hashlib.sha1()
        async for data in self.download_save_stream(src_url, dest_file, chunk_size=65536):
            sha1.update(data)

        sha1 = sha1.hexdigest()

        sha1_dest_file = Path(dest_folder)
        sha1_dest_file = sha1_dest_file / sha1
        sha1_dest_file = sha1_dest_file.with_suffix('.' + ext)

        await dest_file.rename(sha1_dest_file)

        return DownloadResult(filename=sha1_dest_file.__str__(), ext=ext, sha1=sha1)
