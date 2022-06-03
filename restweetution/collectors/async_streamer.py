import aiohttp
import httpx
import asyncio

import json
from typing import Union, List, Dict

import requests

from restweetution.collectors.async_collector import AsyncCollector
from restweetution.models.bulk_data import BulkData
from restweetution.models.tweet import TweetResponse, RestTweet
from restweetution.models.stream_rule import StreamRule, RuleResponse
from restweetution.storage.async_storage_manager import AsyncStorageManager


class AsyncStreamer(AsyncCollector):
    def __init__(self, storage_manager: AsyncStorageManager, config: Union[dict, str]):
        super(AsyncStreamer, self).__init__(storage_manager, config)
        self._fetch_minutes = False
        # use a cache to store the rules
        self.rule_cache: Dict[str, StreamRule] = {}

    async def get_rules(self, ids: List[str] = None) -> List[StreamRule]:
        """
        Return the list of rules defined to collect tweets during a stream
        Once fetched with the API, the rules are cached
        :param ids: an optional list of ids to fetch only specific rules
        :return: the list of rules
        """
        if not self.rule_cache or self._rule_is_missing(ids):
            await self._load_rule_cache()

        rules = self.rule_cache.values()
        if ids:
            rules = [r for r in rules if r.id in ids]
        return rules

    async def get_rule(self, r_id: str) -> StreamRule:
        res = await self.get_rules([r_id])
        return res[0]

    def _rule_is_missing(self, ids):
        if not self.rule_cache:
            return True
        if not ids:
            return False
        for i in ids:
            if not self.rule_cache[i]:
                return True
        return False

    async def _api_get_rules(self, ids: List[str] = None):
        """
        Return the list of rules defined to collect tweets during a stream
        from the Twitter API
        :param ids: an optional list of ids to fetch only specific rules
        :return: the list of rules
        """

        uri = "tweets/search/stream/rules"
        if ids:
            uri += f"?ids={','.join(ids)}"
        async with self._client.get(uri) as resp:
            res = await resp.json()
            if not res.get('data'):
                res['data'] = []
            res = RuleResponse(**res)
            # print(res)
            return res.data

    async def reset_stream_rules(self) -> None:
        """
        Removes all rules
        """
        # self._logger('Removing all rules')
        await self._load_rule_cache()
        if not self.rule_cache:
            return
        ids = [r.id for r in self.rule_cache.values()]
        await self.remove_stream_rules(ids)

    async def set_stream_rules(self, rules: Dict[str, str]) -> List[StreamRule]:
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

        res = await self.add_stream_rules({rule: tag})
        return res[0]

    async def add_stream_rules(self, rule_definitions: Dict[str, str]) -> List[StreamRule]:
        rules = []
        # convert to Twitter api Rule format
        for t, r in rule_definitions.items():
            rules.append({
                "tag": t,
                "value": r
            })
        # make api call
        new_rules = await self._api_add_rules(rules)

        # add new rules to cache
        for r in new_rules:
            self.rule_cache[r['id']] = r
            self._logger.info(f'Cached rule: {r["tag"]}')
        return new_rules

    async def _api_add_rules(self, rules):
        uri = "tweets/search/stream/rules"
        async with self._client.post(uri, json={
            "add": rules
        }) as r:
            res = await r.json()
            valid_rules = []
            if 'errors' in res:
                errs = res['errors']
                for err in errs:
                    self._logger.info(f"_api_add_rules Error: {err['title']} Rule: {err['value']}")
            if 'data' in res:
                valid_rules = res['data']
            return valid_rules

    async def remove_stream_rules(self, ids: List[str]) -> None:
        deleted_ids = await self._api_remove_rules(ids)
        # if no ids return an error occurred
        # We have no information over the remaining rules
        # Force reload of cache to assure data integrity
        if len(deleted_ids) == 0:
            await self._load_rule_cache()
        else:
            for r_id in deleted_ids:
                self.rule_cache.pop(r_id)

    async def _load_rule_cache(self):
        self._logger.info('Load Stream Rules from API into cache')
        rules = await self._api_get_rules()
        self.rule_cache = {}
        for r in rules:
            self.rule_cache[r.id] = r

    async def _api_remove_rules(self, ids: List[str]):
        """
                Remove rules by ids
                :param ids: a list of ids of rules to remove
                """

        uri = "tweets/search/stream/rules"
        async with self._client.post(uri, json={
            "delete": {
                "ids": ids
            }
        }) as r:
            res = await r.json()

            # if everything went fine we return the ids of the deleted rules
            if "errors" not in res:
                self._logger.info(f'Removed {res["meta"]["summary"]["deleted"]} rule(s)')
                return ids

            # if not, return no ids as we can't know what rule failed or not
            self._logger.error(res)
            return []

    # def add_storage_rule(self, rule: Dict[str, List[str]]):
    #
    #
    def _log_tweets(self, tweet: TweetResponse):
        self.tweets_count += 1
        # if self._config.verbose:
        #     self._logger.info(tweet.data.text)
        if self.tweets_count % 10 == 0:
            self._logger.info(f'{self.tweets_count} tweets collected')

    async def _handle_tweet_response(self, tweet_res: TweetResponse):
        self._log_tweets(tweet_res)
        bulk_data = BulkData()

        # Get the full rule from the id in matching_rules
        rules_ref = tweet_res.matching_rules
        rules_id = [r.id for r in rules_ref]
        rules = await self.get_rules(rules_id)
        tags = [r.tag for r in rules]
        bulk_data.rules = rules
        # await self._storages_manager.save_rules(rules)

        # Save user is expanded data is available
        if tweet_res.includes and tweet_res.includes.users:
            bulk_data.users = tweet_res.includes.users
            # await self._storages_manager.save_users(tweet_res.includes.users, tags)

        # We save rules that triggered this tweet inside the tweet data to make sure we don't lose it
        tweet = RestTweet(**tweet_res.data.dict())
        tweet.matching_rules = rules
        # Send the full data to the storages
        bulk_data.tweets = [tweet]
        # await self._storages_manager.save_tweet(tweet, tags)

        self._storages_manager.bulk_save(bulk_data, tags)
        # await self._save_media(tweet_res)

    # async def _save_media(self, tweet_res: TweetResponse):
    #     tags = list(set([r.tag for r in tweet_res.matching_rules]))
    #     # save media if there are some
    #     if tweet_res.includes and tweet_res.includes.media:
    #         await self._storages_manager.save_media(tweet_res.includes.media, tweet_res.data.id, tags)

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

    async def collect(self, fetch_minutes: int = False):
        """
        Main method to collect tweets in a stream
        :param fetch_minutes: if you have a pro or an academic account, you can specify
        an int between 1 and 5 to tell the stream to fetch tweets from the past minutes.
        :return:
        """
        super().collect()
        self._fetch_minutes = fetch_minutes
        # check if some rules are configured
        rules = await self.get_rules()
        if len(rules) == 0:
            self._logger.warning("Stream started but no rules are configured currently, use add_rule to add a new_rule")
        else:
            self._logger.info(f"Collecting with following rules: ")
            self._logger.info('\n'.join([f'{r.value}, tag: {r.tag} id: {r.id}' for r in rules]))
        params = self._create_params_from_config()
        if self._fetch_minutes:
            params = {**params, 'backfill_minutes': self._fetch_minutes}

        try:
            async with self._client.get("tweets/search/stream",
                                        params=params,
                                        timeout=5000
                                        ) as resp:
                async for line in resp.content:
                    if line:
                        txt = line.decode("utf-8")
                        if txt != '\r\n':
                            data = json.loads(txt)
                            self._logger.info(data)
                            if "errors" in data:
                                self._handle_errors(data['errors'])
                            tweet_res = TweetResponse(**data)
                            asyncio.create_task(self._handle_tweet_response(tweet_res))
                    else:
                        self._logger.info("waiting for new tweets")
        except aiohttp.ClientError as e:
            self._logger.error(e)
            self._retry_count += 1
            if self._retry_count < self._config.max_retries:
                self._logger.error("""The collect will try to start again in 30s""")
                await asyncio.sleep(30)
                await self.collect(fetch_minutes)
