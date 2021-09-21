import json
import logging
from typing import Union

import yaml

from restweetution.collectors.client import Client
from restweetution.models.config import Config
from restweetution.storage.storage_provider import storage_provider


class Collector:
    def __init__(self, config: Union[dict, str]):
        """
        Class to define the mains methods of the different collectors (stream, search)
        It should not be instantiated on its own
        :param config: either a dict containing the config, or a path to a json or yaml
        only the token field is mandatory, if no tweet config is provided,
        the restweetution.models.examples_config.BASIC_CONFIG will be used
        """
        self.tweets_count = 0
        self._config = self.resolve_config(config)
        self._tweet_storage = storage_provider(self._config.tweetStorage)
        self._media_storage = storage_provider(self._config.mediaStorage)
        self._client = Client(config=self._config, url_base="https://api.twitter.com/2/")
        self.__logger = logging.getLogger("Collector")

    @staticmethod
    def resolve_config(config_param) -> Config:
        """
        Utility method to automatically transform the config_param in valid config object
        :param config_param: either a dict containing the config, or a path to a json or yaml
        :return: a Config objectA
        """
        if isinstance(config_param, dict):
            return Config(**config_param)
        elif isinstance(config_param, str) and config_param.split('.')[-1] == 'json':
            try:
                with open(config_param, 'r') as f:
                    return Config(**json.load(f))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON provided, the following error occurred trying to open the config: {e}")
        elif isinstance(config_param, str) and config_param.split('.')[-1] == 'yaml':
            try:
                with open(config_param, 'r') as f:
                    return Config(**yaml.safe_load(f))
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML provided, the following error occurred trying to open the config: {e}")
        else:
            raise ValueError("Invalid config provided")

    def _create_params_from_config(self):
        params = {}
        params_config = self._config.tweetConfig
        if params_config.expansions:
            params['expansions'] = params_config.expansions
        if params_config.tweetFields:
            params['tweet.fields'] = params_config.tweetFields
        if params_config.userFields:
            params['user.fields'] = params_config.userFields
        if params_config.mediaFields:
            params['media.fields'] = params_config.mediaFields
        return params

    def _has_free_space(self):
        return self._tweet_storage.has_free_space() and self._media_storage.has_free_space()

    def collect(self):
        self.__logger.info(f"""
            Starting to collect tweets
            Tweets stored at: {self._tweet_storage.root_directory}
            Media stored at: {self._media_storage.root_directory}
        """)

