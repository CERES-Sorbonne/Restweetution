from typing import Callable
from urllib.parse import urljoin

import aiohttp


class AsyncClient(aiohttp.ClientSession):
    def __init__(self, token: str, base_url: str = "https://api.twitter.com/2/", error_handler: Callable = None):
        super().__init__()
        self.base_url = base_url
        self.headers.update({"Authorization": f"Bearer {token}"})
        self.error_handler = error_handler

    def _request(self, method, url, **kwargs):
        modified_url = urljoin(self.base_url, url)
        try:
            res = super()._request(method, modified_url, **kwargs)
            return res
        except aiohttp.ClientResponseError as e:
            self.error_handler(str(e), e.message)
