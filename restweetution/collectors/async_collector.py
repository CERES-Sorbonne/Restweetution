import json
import logging
import time
from enum import Enum
from typing import Union

import yaml

from restweetution.collectors.async_client import AsyncClient
from restweetution.models.stream_config import StreamConfig
from restweetution.models.tweet import TweetResponse
from restweetution.storage.async_storages_manager import AsyncStoragesManager


class AsyncCollector:
    def __init__(self, config: Union[dict, str]):
        """
        Class to define the mains methods of the different collectors (stream, search)
        It should not be instantiated on its own
        :param config: either a dict containing the config, or a path to a json or yaml
        only the token field is mandatory, if no tweet config is provided,
        the restweetution.models.examples_config.BASIC_CONFIG will be used
        """
        self.tweets_count = 0
        self._retry_count = 0
        self._config = self.resolve_config(config)
        self._storages_manager = AsyncStoragesManager(tweets_storages=self._config.tweets_storages,
                                                      media_storages=self._config.media_storages,
                                                      download_media=self._config.download_media,
                                                      average_hash=self._config.average_hash
                                                      )
        self._client = self._client = AsyncClient(config=self._config, base_url="https://api.twitter.com/2/",
                                   error_handler=self._error_handler)
        self._logger = logging.getLogger("Collector")

    # async def init_client(self):
    #     self._client = AsyncClient(config=self._config, base_url="https://api.twitter.com/2/",
    #                                error_handler=self._error_handler)

    @staticmethod
    def resolve_config(config_param) -> StreamConfig:
        """
        Utility method to automatically transform the config_param in valid config object
        :param config_param: either a dict containing the config, or a path to a json or yaml
        :return: a Config objectA
        """
        if isinstance(config_param, dict):
            return StreamConfig(**config_param)
        elif isinstance(config_param, str) and config_param.split('.')[-1] == 'json':
            try:
                with open(config_param, 'r') as f:
                    return StreamConfig(**json.load(f))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON provided, the following error occurred trying to open the config: {e}")
        elif isinstance(config_param, str) and config_param.split('.')[-1] == 'yaml':
            try:
                with open(config_param, 'r') as f:
                    return StreamConfig(**yaml.safe_load(f))
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML provided, the following error occurred trying to open the config: {e}")
        else:
            raise ValueError("Invalid config provided")

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

    def _handle_media(self, tweet: TweetResponse):
        class Media(Enum):
            PHOTO = 1
            VIDEO = 2
            GIF = 3

            def __eq__(self, other):
                if isinstance(other, str):
                    return self.name.lower() == other

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
