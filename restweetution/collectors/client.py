import requests
from urllib.parse import urljoin

from restweetution.models.config import Config


class Client(requests.Session):
    def __init__(self, config: Config = None, base_url = ""):
        super().__init__()
        self.base_url = base_url
        self.headers.update({"Authorization": f"Bearer {config.token}"})

    def request(self, method, url, *args, **kwargs):
        path = urljoin(self.base_url, url)
        return super().request(method, path, *args, **kwargs)
