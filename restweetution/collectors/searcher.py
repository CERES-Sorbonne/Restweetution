from typing import Dict, Union

from restweetution.collectors import Collector
from restweetution.twitter_client import TwitterClient
from restweetution.models.tweet_config import QueryParams
from restweetution.storage.storage_manager import StorageManager


class Searcher(Collector):
    def __init__(self, client: TwitterClient, storage_manager: StorageManager, verbose: bool = False):
        """
        The Searcher is used to make requests to the regular REST API
        """
        # Member declaration before super constructor
        self._params = {}
        self._rule = None
        self._tag = None
        self._preset_stream_rules = None  # used to preset rules in non-async context (config)

        super(Collector, self).__init__(client, storage_manager, verbose=verbose)

    def set_rule(self, rule: str, tag: str):
        self._rule = rule
        self._tag = tag

    def set_dates(self, start=None, end=None):
        if start:
            self._params['start_time'] = start
        if end:
            self._params['end_time'] = end

    def set_params(self, params: Union[Dict, QueryParams]):
        if isinstance(params, dict):
            parsed_params = QueryParams(**params).dict()
        else:
            parsed_params = params.dict()
        self._params = parsed_params

    def count(self):
        """
        Use this method to know how much data will be fetched by the searcher
        """
        pass

    async def collect(self):
        super(Searcher, self).collect()
        if not self._rule:
            self._logger('No rule is set, please use set_rule before using collect')
            return
        pass