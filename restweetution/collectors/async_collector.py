import logging
import time

from restweetution.collectors.async_client import AsyncClient
from restweetution.models.tweet_config import QueryParams
from restweetution.storage.async_storage_manager import AsyncStorageManager


class AsyncCollector:
    def __init__(self,
                 client: AsyncClient,
                 storage_manager: AsyncStorageManager,
                 verbose: bool = False,
                 max_retries: int = 10):
        """
        Class to define the mains methods of the different collectors (stream, search)
        It should not be instantiated on its own
        only the token field is mandatory, if no tweet config is provided,
        the restweetution.models.examples_config.BASIC_CONFIG will be used
        """
        self._params = {}
        self.tweets_count = 0
        self._max_retries = max_retries
        self._retry_count = 0
        self._storages_manager = storage_manager
        self._client = client
        self._verbose = verbose

        self._client.set_error_handler(self._error_handler)
        self._logger = logging.getLogger("Collector")

    def set_query_params(self, query_params: QueryParams):
        if query_params.expansions:
            self._params['expansions'] = ",".join(query_params.expansions)
        if query_params.tweetFields:
            self._params['tweet.fields'] = ",".join(query_params.tweetFields)
        if query_params.userFields:
            self._params['user.fields'] = ",".join(query_params.userFields)
        if query_params.mediaFields:
            self._params['media.fields'] = ",".join(query_params.mediaFields)
        if query_params.placeFields:
            self._params['place.fields'] = ",".join(query_params.placeFields)
        if query_params.pollFields:
            self._params['poll.fields'] = ','.join(query_params.pollFields)

    # def _handle_media(self, tweet: TweetResponse):
    #     class Media(Enum):
    #         PHOTO = 1
    #         VIDEO = 2
    #         GIF = 3
    #
    #         def __eq__(self, other):
    #             if isinstance(other, str):
    #                 return self.name.lower() == other

    def set_verbose(self, value: bool):
        self._verbose = value

    def _error_handler(self, error: str, status_code: int):
        self._logger.error(f"A new http error occurred with status: {status_code}, {error}")
        self._retry_count += 1
        if self._retry_count < self._max_retries:
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
            Log tweets: {self._verbose}
        """)
