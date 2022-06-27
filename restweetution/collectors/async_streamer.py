import asyncio
import json
from typing import List, Dict

import aiohttp
import requests

from restweetution.collectors.async_client import AsyncClient
from restweetution.collectors.async_collector import AsyncCollector
from restweetution.models.bulk_data import BulkData
from restweetution.models.stream_rule import StreamRule
from restweetution.models.twitter.tweet import TweetResponse, RestTweet
from restweetution.models.twitter.user import User
from restweetution.storage.async_storage_manager import AsyncStorageManager


class AsyncStreamer(AsyncCollector):
    def __init__(self, client: AsyncClient, storage_manager: AsyncStorageManager, verbose: bool = False):
        # Member declaration before super constructor
        self._params = None
        self._fetch_minutes = False
        self._preset_stream_rules = None  # used to preset rules in non-async context (config)

        super(AsyncStreamer, self).__init__(client, storage_manager, verbose=verbose)

        # use a cache to store the rules
        self._persistent_rule_cache: Dict[str, StreamRule] = {}
        self._active_rule_cache: Dict[str, StreamRule] = {}

    def _cache_persistent_rule(self, rule):
        self._persistent_rule_cache[rule.id] = rule

    def _cache_active_rule(self, rule):
        self._active_rule_cache[rule.id] = rule
        self._cache_persistent_rule(rule)

    def _remove_active_cache_rule(self, r_id):
        self._active_rule_cache.pop(r_id)

    def set_backfill_minutes(self, backfill_minutes: int):
        # compute request parameters
        self._params['backfill_minutes'] = backfill_minutes

    async def get_active_rules(self) -> List[StreamRule]:
        """
        Return the list of rules defined to collect tweets during a stream
        Once fetched with the API, the rules are cached
        :return: the list of rules
        """
        if not self._active_rule_cache:
            await self._load_rule_cache()

        return list(self._active_rule_cache.values())

    async def get_rules_from_cache(self, ids):
        if not self._persistent_rule_cache or self._rule_is_missing(ids):
            await self._load_rule_cache()

        rules = self._persistent_rule_cache.values()
        if ids:
            rules = [r for r in rules if r.id in ids]
        return rules.copy()

    def _rule_is_missing(self, ids):
        if not self._persistent_rule_cache:
            return True
        if not ids:
            return False
        for i in ids:
            if i not in self._persistent_rule_cache:
                return True
        return False

    async def reset_stream_rules(self) -> None:
        """
        Removes all rules
        """
        # self._logger('Removing all rules')
        await self._load_rule_cache()
        if not self._persistent_rule_cache:
            return
        ids = [r.id for r in self._persistent_rule_cache.values()]
        await self.remove_stream_rules(ids)

    def pre_set_stream_rules(self, rules: List[Dict[str, str]]):
        self._preset_stream_rules = rules

    async def set_stream_rules(self, rules: List[Dict[str, str]]) -> List[StreamRule]:
        """
        Like add_rule but instead removes all rules and then set the rules :rules:
        :param rules: a dict in the form tag: rule
        :return: the list of all the new rules
        """
        await self.reset_stream_rules()
        res = await self.add_stream_rules(rules)
        return res

    async def add_stream_rule(self, rule: str, tag: str) -> StreamRule:
        """
        Add a new fetch rule to the stream
        :param rule: the rule to be created, for more info on the syntax check
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
        :param tag: the tag associated to the rule, all tweets collected with those rules will be stored under the
        <tag> folder
        so if you have different rules with the same tag,
        all this rules will collect tweets that will be grouped in one place
        :return: the id of the created rule (can be used to delete the rule later)
        """

        res = await self.add_stream_rules([{'tag': tag, 'value': rule}])
        return res[0]

    async def add_stream_rules(self, rule_definitions: List[Dict[str, str]]) -> List[StreamRule]:
        # make api call
        new_rules = await self._client.add_rules(rule_definitions)

        # add new rules to cache
        for r in new_rules:
            rule = StreamRule(**r)
            self._cache_active_rule(rule)
            self._logger.info(f'Cached rule: {r["tag"]}')
        return new_rules

    async def remove_stream_rules(self, ids: List[str]) -> None:
        deleted_ids = await self._client.remove_rules(ids)
        # if no ids return an error occurred
        # We have no information over the remaining rules
        # Force reload of cache to assure data integrity
        if len(deleted_ids) == 0:
            await self._load_rule_cache()
        else:
            for r_id in deleted_ids:
                self._remove_active_cache_rule(r_id)

    async def _load_rule_cache(self):
        self._logger.info('Load Stream Rules from API into cache')
        rules = await self._client.get_rules()
        self._persistent_rule_cache = {}
        for r in rules:
            self._cache_active_rule(r)

    # def add_storage_rule(self, rule: Dict[str, List[str]]):
    #
    #
    def _log_tweets(self, tweet: TweetResponse):
        self.tweets_count += 1
        if self._verbose:
            text = tweet.data.text.split('\n')[0]
            if len(text) > 80:
                text = text[0:80] + '..'
            self._logger.info(f'id: {tweet.data.id} - {text}')
        if self.tweets_count % 10 == 0:
            self._logger.info(f'{self.tweets_count} tweets collected')

    @staticmethod
    def set_from_list(target: dict, key: str, array: list):
        for item in array:
            target[item.dict()[key]] = item

    async def _handle_tweet_response(self, tweet_res: TweetResponse):
        self._log_tweets(tweet_res)
        bulk_data = BulkData()

        # Get the full rule from the id in matching_rules
        rules_ref = tweet_res.matching_rules
        rule_ids = [r.id for r in rules_ref]

        rules = await self.get_rules_from_cache(rule_ids)
        tags = [r.tag for r in rules]

        for r in rules:
            r.tweet_ids = [tweet_res.data.id]
        self.set_from_list(bulk_data.rules, 'id', rules)

        # await self._storages_manager.save_rules(rules)

        # Save user is expanded data is available
        if tweet_res.includes:
            if tweet_res.includes.users:
                self.set_from_list(bulk_data.users, 'id', tweet_res.includes.users)
            if tweet_res.includes.places:
                self.set_from_list(bulk_data.places, 'id', tweet_res.includes.places)
            if tweet_res.includes.media:
                self.set_from_list(bulk_data.media, 'media_key', tweet_res.includes.media)
            if tweet_res.includes.polls:
                self.set_from_list(bulk_data.polls, 'id', tweet_res.includes.polls)

        # Convert to RestTweet standard
        tweet = RestTweet(**tweet_res.data.dict())
        # Enrich data by de-normalizing some fields
        self._enrich_tweet(tweet, bulk_data.rules, bulk_data.users)
        # Save into bulk_data
        self.set_from_list(bulk_data.tweets, 'id', [tweet])

        # send data to storage manager
        self._storages_manager.bulk_save(bulk_data, tags)
        # await self._save_media(tweet_res)

    # async def _save_media(self, tweet_res: TweetResponse):
    #     tags = list(set([r.tag for r in tweet_res.matching_rules]))
    #     # save media if there are some
    #     if tweet_res.includes and tweet_res.includes.media:
    #         await self._storages_manager.save_media(tweet_res.includes.media, tweet_res.data.id, tags)

    @staticmethod
    def _enrich_tweet(tweet: RestTweet, rules: Dict[str, StreamRule], users: Dict[str, User]):

        # We save rules that triggered the tweets inside the tweet data to make sure we don't lose it
        tweet.matching_rules = [rules[key] for key in rules]

        # If user data is given we add author username to tweet
        if tweet.author_id:
            if tweet.author_id in users:
                tweet.author_username = users[tweet.author_id].username

    def _handle_errors(self, errors: List[dict]) -> None:
        """
        Some errors might still be wrapped in a 200 response
        So they need to be handled manually and not in Collector._error_handler
        which will only be triggered for responses > 299
        :param errors: a list of errors dictionary
        """
        for error in errors:
            self._logger.error(f"""The following error was encountered: {error}""")
        if errors[0]['title'] in ['Authorization Error', 'Forbidden']:
            # Authorization Error: the data is private
            # Forbidden: the user is probably suspended
            # in all those cases we continue to collect, it's not a twitter blocking the connection
            return
        else:
            raise requests.RequestException()

    def _handle_line_response(self, line: bytes):
        if line:
            txt = line.decode("utf-8")
            if txt != '\r\n':
                data = json.loads(txt)
                if "errors" in data:
                    self._handle_errors(data['errors'])
                tweet_res = TweetResponse(**data)
                asyncio.create_task(self._handle_tweet_response(tweet_res))
        else:
            self._logger.info("waiting for new tweets")

    async def collect(self):
        """
        Main method to collect tweets in a stream
        an int between 1 and 5 to tell the stream to fetch tweets from the past minutes.
        """
        super().collect()

        # if rules are preset, set them now
        if self._preset_stream_rules:
            await self.set_stream_rules(self._preset_stream_rules)
            self._preset_stream_rules = None
        # check if some rules are configured
        rules = await self.get_active_rules()
        if len(rules) == 0:
            self._logger.warning("Stream started but no rules are configured currently, use add_rule to add a new_rule")
        else:
            self._logger.info(f"Collecting with following rules: ")
            self._logger.info('\n'.join([f'{r.value}, tag: {r.tag} id: {r.id}' for r in rules]))

        try:
            await self._client.connect_tweet_stream(self._params, self._handle_line_response)
        except aiohttp.ClientConnectorError as e:
            self._logger.error(e)
            self._retry_count += 1
            if self._retry_count < self._max_retries:
                self._logger.error("""The collect will try to start again in 30s""")
                await asyncio.sleep(30)
                await self.collect()
