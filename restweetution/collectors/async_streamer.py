import aiohttp
import asyncio

import json
from typing import Union, List, Dict, Optional

import requests

from restweetution.models.rule import RuleResponse, Rule
from restweetution.models.user import User
from restweetution.collectors.async_collector import AsyncCollector
from restweetution.models.tweet import TweetResponse, RuleLink, StreamRule, RestTweet


class AsyncStreamer(AsyncCollector):
    def __init__(self, config: Union[dict, str]):
        super(AsyncStreamer, self).__init__(config)
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
        uri = "tweets/search/stream/rules"
        return await self._api_get_rules()
        # if ids:
        #     ids_to_fetch = list(set(ids) - set(self.rule_cache.keys()))
        #     # first get missing rules  with api and set them in cache
        #     if ids_to_fetch:
        #         uri += f"?ids={','.join(ids_to_fetch)}"
        #         res = await self._client.get(uri)
        #         for r in res.json().get('data', []):
        #             rule = StreamRule(**r)
        #             self.rule_cache[rule.id] = rule
        #     # then return the cached rules
        #     return [self.rule_cache.get(rid) for rid in ids]
        # else:
        #     if len(self.rule_cache.keys()) == 0:
        #         res = await self._client.get(uri)
        #         # TODO: maybe find a way to avoid writing this code here too since it's already in the if ids part ?
        #         for r in res.json().get('data', []):
        #             rule = StreamRule(**r)
        #             self.rule_cache[rule.id] = rule
        #     # use this syntax to avoid pycharm typing error
        #     return [*self.rule_cache.values()]

    async def _api_get_rules(self, ids: Optional[List[str]] = []):
        """
        Return the list of rules defined to collect tweets during a stream
        from the Twitter API
        :param ids: an optional list of ids to fetch only specific rules
        :return: the list of rules
        """

        uri = "tweets/search/stream/rules"
        if len(ids) > 0:
            uri += f"?ids={','.join(ids)}"
        async with self._client.get(uri) as r:
            res = await r.json()
            if not res.get('data'):
                res['data'] = []
            res = RuleResponse(**res)
            # print(res)
            return res.data

    async def reset_rules(self) -> None:
        """
        Removes all rules
        """
        # self._logger('Removing all rules')
        ids = [r.id for r in await self._api_get_rules()]
        await self.remove_rules(ids)

    async def set_rules(self, rules: Dict[str, str]) -> List[str]:
        """
        Like add_rule but instead removes all rules and then set the rules :rules:
        :param rules: a dict in the form tag: rule
        :return: the list of ids of all new rules
        """
        existing_rules = await self.get_rules()
        existing_values = [r.value for r in existing_rules]
        rules_to_remove = []
        res = []
        for existing_rule in existing_rules:
            # check if an old rule has to be deleted because it's no longer in the rules param
            if existing_rule.value not in rules.values():
                rules_to_remove.append(existing_rule.id)
            # check if among the new_rules, some are already existing
        for new_tag, new_rule in rules.items():
            if new_rule not in existing_values:
                res.append(self.add_rule(new_rule, new_tag))
        return res

    async def add_rule(self, rule: str, tag: str) -> Rule:
        """
        Add a new fetch rule to the stream
        :param rule: the rule to be created, for more info on the syntax check
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
        :param tag: the tag associated to the rule, all tweets collected with those rules will be stored under the
        <tag> folder
        so if you have different rules with the same tag, all this rules will collect tweets that will be grouped in one place
        :return: the id of the created rule (can be used to delete the rule later)
        """

        res = await self.add_rules({rule: tag})
        return res[0]

    async def add_rules(self, rule_definitions: dict) -> List[Rule]:
        rules = []
        # convert to twitter api Rule format
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

    async def remove_rules(self, ids: List[str]) -> None:
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
            if "errors" in res:
                raise ValueError(f"The following errors happened while trying to delete "
                                 f"the rule: {res['errors'][0]['errors']['message']}")
            else:
                self._logger.info(f'Removed {res["meta"]["summary"]["deleted"]} rule(s)')

    def _log_tweets(self, tweet: TweetResponse):
        self.tweets_count += 1
        if self._config.verbose:
            self._logger.info(tweet.data.text)
        if self.tweets_count % 10 == 0:
            self._logger.info(f'{self.tweets_count} tweets collected')

    async def _save_rules(self, rules: List[RuleLink]) -> None:
        """
        Get every stored rule, and if some rules of the current tweets
        are not stored currently, get full rule and store it
        Since rules are Streamer specific this method cannot be fully in the storage manager
        :param rules: the matching rules of the collected data
        """
        tags = [r.tag for r in rules]
        ids = [r.id for r in rules]
        ids_to_store = self._storages_manager.get_non_existing_rules(ids=ids, tags=tags)
        if ids_to_store:
            if self._config.verbose:
                self._logger.info(f"Storing new rules: {ids_to_store}")
            # TODO: make async
            self._storages_manager.save_rules(self.get_rules(ids=ids_to_store))

    async def _save_user(self, user: [User]):
        """
        get users in data
        check if users in data have all their data stored in storage
        if new user then save it, question => save only currently available data or do a get /user to get all data
        :param user:
        :return:
        """
        pass

    async def _handle_tweet_response(self, tweet_res: TweetResponse):
        self._log_tweets(tweet_res)
        # make sure rules are already saved
        await self._save_rules(tweet_res.matching_rules)
        # save user info if there are some:
        await self._save_user(tweet_res.includes.users)
        # save data and media asynchronously
        await self._save_tweet(tweet_res)

    async def _save_tweet(self, tweet_res: TweetResponse):
        """
        save tweet from the tweet_response to storage
        the matching_rules are added to the tweet object
        """
        # get all tags associated to the data
        tags = list(set([r.tag for r in tweet_res.matching_rules]))
        # save media if there are some
        if tweet_res.includes and tweet_res.includes.media:
            await self._storages_manager.save_media(tweet_res.includes.media, tweet_res.data.id, tags)
        # change from TweetResponse to RestTweet object
        to_save = RestTweet(**tweet_res.data.dict())
        to_save.matching_rules = tweet_res.matching_rules

        await self._storages_manager.save_tweets([to_save], tags)

    def _handle_errors(self, errors: List[dict], *args) -> None:
        """
        Some errors might still be wrapped in a 200 response
        So they need to be handled manually and not in Collector._error_handler
        which will only be triggered for responses > 299
        :param errors: a list of errors dictionary
        :param args: the arguments to pass to collect when retrying
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

    async def collect(self, sub_process: bool = False, fetch_minutes: int = False):
        """
        Main method to collect tweets in a stream
        :param sub_process: should the collect be run in a subprocess ?
        :param fetch_minutes: if you have a pro or an academic account, you can specify
        an int between 1 and 5 to tell the stream to fetch tweets from the past minutes.
        :return:
        """
        super().collect()
        self._fetch_minutes = fetch_minutes
        # check if some rules are configured
        rules = self.get_rules()
        if len(rules) == 0:
            self._logger.warning("Stream started but no rules are configured currently, use add_rule to add a new_rule")
        else:
            self._logger.info(f"Collecting with following rules: ")
            self._logger.info('\n'.join([f'{r.value}, tag: {r.tag} id: {r.id}' for r in rules]))
        params = self._create_params_from_config()
        if self._fetch_minutes:
            params = {**params, 'backfill_minutes': self._fetch_minutes}
        headers = {"Authorization": f"Bearer {self._config.token}"}
        async with self._client as session:
            try:
                async with session.get(
                        "https://api.twitter.com/2/tweets/search/stream",
                        params=params,
                        timeout=5000
                ) as resp:
                    async for line in resp.content:
                        if line:
                            txt = line.decode("utf-8")
                            self._logger.info(txt)
                            if txt != '\r\n':
                                data = json.loads(txt)
                                # self._logger.info(data)
                                if "errors" in data:
                                    self._handle_errors(data['errors'])
                                tweet_res = TweetResponse(**data)
                                asyncio.create_task(self._handle_tweet_response(tweet_res))
                        else:
                            self._logger.info("waiting for new tweets")
            except aiohttp.ClientConnectorError as e:
                self._logger.error(e)
                self._retry_count += 1
                if self._retry_count < self._config.max_retries:
                    self._logger.error("""The collect will try to start again in 30s""")
                    await asyncio.sleep(30)
                    await self.collect(sub_process, fetch_minutes)
