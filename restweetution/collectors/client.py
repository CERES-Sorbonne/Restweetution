from typing import Callable

import requests
from urllib.parse import urljoin

from restweetution.models.config import Config


class Client(requests.Session):
    def __init__(self, config: Config = None, base_url: str = "", error_handler: Callable = None):
        super().__init__()
        self.base_url = base_url
        self.headers.update({"Authorization": f"Bearer {config.token}"})
        self.error_handler = error_handler

    def request(self, method, url, **kwargs):
        modified_url = urljoin(self.base_url, url)
        try:
            res = super().request(method, modified_url, **kwargs)
            res.raise_for_status()
            return res
        except requests.RequestException as e:
            self.error_handler(str(e), e.response.status_code)
