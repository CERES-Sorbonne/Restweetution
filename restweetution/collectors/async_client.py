from urllib.parse import urljoin
from typing import Callable

import aiohttp

from restweetution.models.stream_config import CollectorConfig


class AsyncClient(aiohttp.ClientSession):
    def __init__(self, config: CollectorConfig = None, base_url: str = "", error_handler: Callable = None):
        super().__init__()
        self.base_url = base_url
        self.headers.update({"Authorization": f"Bearer {config.token}"})
        self.error_handler = error_handler

    async def _request(self, method, url, **kwargs):
        modified_url = urljoin(self.base_url, url)
        try:
            res = await super()._request(method, modified_url, **kwargs)
            return res
        except aiohttp.ClientError as e:
            self.error_handler(str(e), "Error when trying to perform request")