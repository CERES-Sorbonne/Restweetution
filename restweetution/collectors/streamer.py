import asyncio
import datetime
import json
import logging
import traceback
from typing import List, Dict

from restweetution.collectors.response_parser import parse_includes
from restweetution.errors import ResponseParseError, TwitterAPIError, StorageError, set_error_handler, handle_error, \
    UnreadableResponseError, RESTweetutionError
from restweetution.models.bulk_data import BulkData
from restweetution.models.config.tweet_config import QueryFields
from restweetution.models.storage.error import ErrorModel
from restweetution.models.rule import StreamerRule, StreamAPIRule
from restweetution.models.twitter.tweet import TweetResponse
from restweetution.storage_manager import StorageManager
from restweetution.twitter_client import TwitterClient


class Streamer:
    def __init__(self, bearer_token, storage_manager: StorageManager, verbose: bool = False):
        """
        The Streamer is the class used to connect to the Twitter Stream API and fetch live tweets
        """
        # Member declaration before super constructor
        self._params = None
        self._fetch_minutes = False
        self._preset_stream_rules = None  # used to preset rules in non-async context (config)

        # super(Streamer, self).__init__(client, storage_manager, verbose=verbose)

        # use a cache to store the rules
        # cache twitter rule api id to local StreamerRule object
        self._api_id_to_rule: Dict[str, StreamerRule] = {}
        # dict of active rules
        self._active_rules: Dict[int, StreamerRule] = {}

        # self._client2 = AsyncStreamingClient(bearer_token=bearer_token)
        self._client = TwitterClient(token=bearer_token)

        self._storage_manager = storage_manager

        self._logger = logging.getLogger('Streamer')
        self._tweet_count = 0
        self._verbose = verbose

        set_error_handler(self._main_error_handler)

    def set_backfill_minutes(self, backfill_minutes: int):
        # compute request parameters
        self._params['backfill_minutes'] = backfill_minutes

    def get_rules(self) -> List[StreamerRule]:
        """
        Return the list of active rules defined to collect tweets during a stream
        :return: the list of rules
        """
        return list(self._active_rules.values())

    async def get_api_rules(self):
        """
        Return the rules registered on the api
        :return: list of API Rules
        """
        return await self._client.get_rules()

    async def reset_stream_rules(self) -> None:
        """
        Removes all rules
        """
        await self.remove_rules([r.id for r in self.get_rules()])

    async def set_rules(self, rules: List[StreamerRule]) -> List[StreamerRule]:
        """
        Like add_rule but instead removes all rules and then set the rules :rules:
        :param rules: a dict in the form tag: rule
        :return: the list of all the new rules
        """

        self._clear_rule_cache()
        self._active_rules = {}
        await self.add_rules(rules)
        server_rules = await self.get_api_rules()
        api_ids_to_del = [rule.id for rule in server_rules if rule.id not in self._api_id_to_rule]
        if api_ids_to_del:
            await self._client.remove_rules(api_ids_to_del)

        return self.get_rules()

    def _clear_rule_cache(self):
        self._api_id_to_rule = {}

    async def add_rules(self, rules: List[StreamerRule]) -> List[StreamerRule]:
        rules = await self._storage_manager.request_rules(rules)
        rules_to_add: List[StreamerRule] = [r for r in rules if r.id not in self._active_rules]

        server_rules = await self.get_api_rules()

        hash_to_server_rule = {r.tag_value_hash(): r for r in server_rules}

        for rule in rules_to_add:
            hash_ = rule.tag_query_hash()
            if hash_ in hash_to_server_rule:
                rule.api_id = hash_to_server_rule[hash_].id
            else:
                s_rule = await self._client.add_rules([rule.get_api_rule()])
                if not s_rule:
                    continue
                rule.api_id = s_rule[0].id

            self._cache_rules([rule])
            self._active_rules[rule.id] = rule
        return list(self._active_rules.values())

    async def remove_rules(self, ids: List[int]):
        rules = [r for r in self.get_rules() if r.id in ids]
        rule_api_ids = [r.api_id for r in rules]
        await self._client.remove_rules(rule_api_ids)

        for rule in rules:
            self._active_rules.pop(rule.id)

    def _cache_rules(self, rules: List[StreamerRule]):
        for rule in rules:
            self._api_id_to_rule[rule.api_id] = rule

    def _get_cache_rules(self, api_keys: List[str]):
        rules = []
        for api_key in api_keys:
            if api_key in self._api_id_to_rule:
                rule = self._api_id_to_rule[api_key].copy()
                if rule.id in self._active_rules:
                    rules.append(rule)
        return rules

    # async def remove_rules(self, ids: List[str]) -> None:
    #     await self._client.remove_rules(ids)
    #     for id_ in ids:
    #         self._api_id_to_rule.pop(id_)

    def _log_tweets(self, tweet: TweetResponse):
        self._tweet_count += 1
        if self._verbose:
            text = tweet.data.text.split('\n')[0]
            if len(text) > 80:
                text = text[0:80] + '..'
            self._logger.info(f'id: {tweet.data.id} - {text}')
        if self._tweet_count % 10 == 0:
            self._logger.info(f'{self._tweet_count} tweets collected')

    async def _main_error_handler(self, error: Exception):
        trace = traceback.format_exc()
        self._logger.exception(trace)
        # self._logger.warning(f'Error: {type(error)}')
        if isinstance(error, RESTweetutionError):
            error_data = ErrorModel(error=error, traceback=trace)
            self._storage_manager.save_error(error_data)

    async def _tweet_response_to_bulk_data(self, tweet_res: TweetResponse):
        """
        Handles one tweet response from the tweet stream
        All data than can be saved with the storage manager is inserted in one bulk_data
        The bulk_data is then given to the storage manager for saving
        :params tweet_res: the tweet response object
        """
        self._log_tweets(tweet_res)

        bulk_data = BulkData()

        # Add collected tweet
        tweet = tweet_res.data
        bulk_data.add_tweets([tweet])

        # Add includes
        bulk_data.add(**parse_includes(tweet_res.includes))

        # Get the full rule from the id in matching_rules
        rules = self._get_cache_rules([r.id for r in tweet_res.matching_rules])

        if not rules:
            self._logger.warning('No rule matched requested rules')
            return

        # Add rules and mark tweet as collected
        bulk_data.add_rules(rules, collected=True)
        return bulk_data

    # def _handle_errors(self, errors: List[dict]) -> None:
    #     """
    #     Some errors might still be wrapped in a 200 response
    #     So they need to be handled manually and not in Collector._error_handler
    #     which will only be triggered for responses > 299
    #     :param errors: a list of errors dictionary
    #     """
    #     for error in errors:
    #         pass
    #         # self._logger.error(f"""The following error was encountered: {error}""")
    #     if errors[0]['title'] in ['Authorization Error', 'Forbidden']:
    #         # Authorization Error: the data is private
    #         # Forbidden: the user is probably suspended
    #         # in all those cases we continue to collect, it's not a twitter blocking the connection
    #         return
    #     else:
    #         raise requests.RequestException()

    @handle_error
    async def _handle_line_response(self, line: bytes):
        """
        Callback for the client tweet stream function.
        Is used to parse the line of bytes into a TweetResponse containing the tweet data
        :param line: bytes to be parsed
        """
        # if line is empty log message
        if not line:
            # self._logger.info("waiting for new tweets")
            return

        # parse to utf-8
        try:
            txt = line.decode('utf-8')
        except Exception as e:
            raise UnreadableResponseError('Failed to parse the server response to utf-8') from e

        # ignore line return
        if txt == '\r\n':
            return

        # try parsing to json
        try:
            data = json.loads(txt)
        except Exception as e:
            raise ResponseParseError('Failed to parse the server response to json', raw_text=txt) from e

        # Parse json object with pydantic
        try:
            tweet_res = TweetResponse(**data)
        except Exception as e:
            # If there is a Twitter API Error we assume the parsing failed because of this. Probably no data
            if 'errors' in data:
                raise TwitterAPIError('Streamer response has error field', data=data)

            raise ResponseParseError('Failed to parse the json response with pydantic', data=data) from e

        # Build BulkData from the TweetResponse containing all objects that can be saved
        try:
            bulk_data = await self._tweet_response_to_bulk_data(tweet_res)
            if not bulk_data:
                return
        except Exception as e:
            raise ResponseParseError('Unexpected Error while building BulkData from the TweetResponse', data=data) \
                from e

        # send data to storage_manager
        try:
            bulk_data.timestamp = datetime.datetime.now()
            self._storage_manager.save_bulk(bulk_data)
        except Exception as e:
            raise StorageError('Unexpected StorageManager bulk_save function error') from e

        # We cast the Twitter api error at the end, so we can save the data that was retrieved before
        if 'errors' in data:
            raise TwitterAPIError('Streamer response has error field', data=data)

    async def collect(self, rules: List[StreamerRule], fields: QueryFields = None):
        """
        Main method to collect tweets in a stream
        an int between 1 and 5 to tell the stream to fetch tweets from the past minutes.
        """
        # super().collect()

        if not fields:
            fields = {}

        await self.set_rules(rules)

        if len(rules) == 0:
            self._logger.warning('No rules are set, close streamer')
            return

        self._logger.info(f"Collecting with following rules: ")
        self._logger.info('\n'.join([f'{r.query}, tag: {r.tag} id: {r.id}' for r in rules]))

        async for line in self._client.connect_tweet_stream(params=fields):
            asyncio.create_task(self._handle_line_response(line))
