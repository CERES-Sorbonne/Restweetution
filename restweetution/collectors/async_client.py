from typing import Callable

import aiohttp
from urllib.parse import urljoin

from restweetution.models.stream_config import StreamConfig


class AsyncClient(aiohttp.ClientSession):
    def __init__(self, config: StreamConfig = None, base_url: str = "", error_handler: Callable = None):
        super().__init__()
        self.base_url = base_url
        self.headers.update({"Authorization": f"Bearer {config.token}"})
        self.error_handler = error_handler

    def _request(self, method, url, **kwargs):
        modified_url = urljoin(self.base_url, url)
        try:
            res = super()._request(method, modified_url, **kwargs)
            return res
        except aiohttp.ClientResponseError as e:
            self.error_handler(str(e), e.message)
