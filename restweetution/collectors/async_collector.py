import logging
import time
from typing import Union, Optional

from restweetution.collectors.async_client import AsyncClient
from restweetution.models.stream_config import StreamConfig
from restweetution.storage.async_storage_manager import AsyncStorageManager


class AsyncCollector:
    def __init__(self, client: AsyncClient, storage_manager: AsyncStorageManager):
        """
        Class to define the mains methods of the different collectors (stream, search)
        It should not be instantiated on its own
        :param config: either a dict containing the config, or a path to a json or yaml
        only the token field is mandatory, if no tweet config is provided,
        the restweetution.models.examples_config.BASIC_CONFIG will be used
        """
        self.tweets_count = 0
        self._retry_count = 0
        self._config: Optional[StreamConfig] = None
        self._storages_manager = storage_manager
        self._client = client

        self._logger = logging.getLogger("Collector")

    def set_query_params(self):
        pass

    def _create_params_from_config(self):
        params = {}
        params_config = self._config.tweet_config
        if params_config.expansions:
            params['expansions'] = ",".join(params_config.expansions)
        if params_config.tweetFields:
            params['tweet.fields'] = ",".join(params_config.tweetFields)
        if params_config.userFields:
            params['user.fields'] = ",".join(params_config.userFields)
        if params_config.mediaFields:
            params['media.fields'] = ",".join(params_config.mediaFields)
        return params

    # def _handle_media(self, tweet: TweetResponse):
    #     class Media(Enum):
    #         PHOTO = 1
    #         VIDEO = 2
    #         GIF = 3
    #
    #         def __eq__(self, other):
    #             if isinstance(other, str):
    #                 return self.name.lower() == other

    def _error_handler(self, error: str, status_code: int):
        self._logger.error(f"A new http error occurred with status: {status_code}, {error}")
        self._retry_count += 1
        if self._retry_count < self._config.max_retries:
            self._logger.warning("Retrying collect in 30s")
            time.sleep(30)
            self.collect()
        else:
            self._logger.warning("Max Retries exceeded, stopping collect")

    def collect(self):
        self._logger.info(f"""
            Starting to collect tweets
            Storages:
            {str(self._storages_manager)}
            Log tweets: {self._config.verbose}
        """)
