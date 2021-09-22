from urllib.parse import urljoin

import requests

from restweetution.models.config import Config


class Client(requests.Session):
    def __init__(self, config: Config, url_base=None):
        """
        Utility class that wraps the default requests.session to provide a base url (here twitter api) for every request
        :param config: a Config object containing the token to pass
        :param url_base: the base url
        """
        super().__init__()
        self.url_base = url_base
        self.headers.update({"Authorization": f"Bearer {config.token}"})

    def request(self, method, url, **kwargs):
        modified_url = urljoin(self.url_base, url)
        try:
            res = super().request(method, modified_url, **kwargs)
            res.raise_for_status()
            return res
        except requests.RequestException as e:
            raise requests.RequestException(f"There was an exception during the twitter call: {e}")
