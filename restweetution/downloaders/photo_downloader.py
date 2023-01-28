import io
import logging

import aiohttp

from restweetution.downloaders.queue_worker import QueueDownloader, DownloadResult
from restweetution.downloaders.utils import compute_signature
from restweetution.storages.object_storage.filestorage_helper import FileStorageHelper

logger = logging.getLogger('PhotoDownloader')


class PhotoDownloader(QueueDownloader):

    def __init__(self, root: str):
        super().__init__(root)
        self._file_helper = FileStorageHelper(root)

    async def _execute(self, url: str):
        try:
            connector = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                media_format = url.split('.')[-1]
                res = await session.get(url)

                bytes_image: bytes = await res.content.read()
                buffer = io.BytesIO(bytes_image)
                sha1 = compute_signature(bytes_image)
                format_ = media_format

                filename = await self._write_photo(buffer, sha1, format_)

                return DownloadResult(filename=filename, sha1=sha1)
        except aiohttp.ClientResponseError as e:
            logger.warning(f"There was an error downloading image {url}: " + str(e))
            return DownloadResult(error=e.__str__())

    async def _write_photo(self, bytes_, name, format_):
        filename = name + '.' + format_
        return await self._file_helper.put(key=filename, buffer=bytes_)
