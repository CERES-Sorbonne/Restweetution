import concurrent.futures
import json
import time
from typing import Union, List, Dict

import requests

from restweetution.collectors.collector import Collector
from restweetution.models.tweet import Tweet, Rule, StreamRule


class Streamer(Collector):
    def __init__(self, config: Union[dict, str]):
        super(Streamer, self).__init__(config)
        self._fetch_minutes = False
        self.executor = concurrent.futures.ThreadPoolExecutor()
        # use a cache to store the rules
        self.rule_cache: Dict[str, StreamRule] = {}

    def get_rules(self, ids: List[str] = None) -> List[StreamRule]:
        """
        Return the list of rules defined to collect tweets during a stream
        Once fetched with the API, the rules are cached
        :param ids: an optional list of ids to fetch only specific rules
        :return: the list of rules
        """
        uri = "tweets/search/stream/rules"
        if ids:
            ids_to_fetch = list(set(ids) - set(self.rule_cache.keys()))
            rules_to_return = []
            # first get missing rules  with api and set them in cache
            if ids_to_fetch:
                uri += f"?ids={','.join(ids_to_fetch)}"
                res = self._client.get(uri)
                for r in res.json().get('data', []):
                    rule = StreamRule(**r)
                    self.rule_cache[rule.id] = rule
            # then return the cached rules
            return [self.rule_cache.get(rid) for rid in ids]
        else:
            if len(self.rule_cache.keys()) == 0:
                res = self._client.get(uri)
                # TODO: maybe find a way to avoid writing this code here too since it's already in the if ids part ?
                for r in res.json().get('data', []):
                    rule = StreamRule(**r)
                    self.rule_cache[rule.id] = rule
            # use this syntax to avoid pycharm typing error
            return [*self.rule_cache.values()]

    def reset_rules(self) -> None:
        """
        Removes all rules
        """
        self._logger('Removing all rules')
        ids = [r.id for r in self.get_rules()]
        for rid in ids:
            self.remove_rule(rid)

    def set_rules(self, rules: Dict[str, str]) -> List[str]:
        """
        Like add_rule but instead removes all rules and then set the rules :rules:
        :param rules: a dict in the form tag: rule
        :return: the list of ids of all new rules
        """
        existing_rules = self.get_rules()
        existing_values = [r.value for r in existing_rules]
        rules_to_remove = []
        res = []
        for existing_rule in existing_rules:
            # check if an old rule has to be deleted cause it's no longer in the rules param
            if existing_rule.value not in rules.values():
                rules_to_remove.append(existing_rule.id)
            # check if among the new_rules, some are already existing
        for new_tag, new_rule in rules.items():
            if new_rule not in existing_values:
                res.append(self.add_rule(new_rule, new_tag))
        return res

    def add_rule(self, rule: str, tag: str) -> str:
        """
        Add a new fetch rule to the stream
        :param rule: the rule to be created, for more info on the syntax check
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
        :param tag: the tag associated to the rule, all tweets collected with this rules will be stored under the <tag> folder
        so if you have different rules with the same tag, all this rules will collect tweets that will be grouped in one place
        :return: the id of the created rule (can be used to delete the rule later)
        """
        res = self._client.post("tweets/search/stream/rules", json={
            "add": [{
                "value": rule,
                "tag": tag
            }]
        })
        if "errors" in res.json():
            if res.json()['errors'][0]['title'] != "DuplicateRule":
                raise ValueError(f"The following errors happened while trying to create "
                                 f"the rule: {res.json()['errors'][0]['details']}")
            else:
                self._logger.warning('This rule already exists')
        else:
            return res.json()['data'][0]['id']

    def remove_rule(self, id_to_remove: Union[str, List[str]]) -> None:
        """
        Remove one or several rules
        :param id_to_remove: the id or a list of ids of rules to remove
        """
        res = self._client.post("tweets/search/stream/rules", json={
            "delete": {
                "ids": [id_to_remove] if isinstance(id_to_remove, str) else id_to_remove
            }

        })
        if "errors" in res.json():
            raise ValueError(f"The following errors happened while trying to delete "
                             f"the rule: {res.json()['errors'][0]['errors']['message']}")
        else:
            self._logger.info(f'Removed rule: {id_to_remove}')

    def _log_tweets(self, tweet: Tweet):
        self.tweets_count += 1
        if self._config.verbose:
            self._logger.info(tweet.data.text)
        if self.tweets_count % 10 == 0:
            self._logger.info(f'{self.tweets_count} tweets collected')

    def _handle_rules(self, rules: List[Rule]) -> None:
        """
        Get every stored rule, and if some rules of the current tweets
        are not stored currently, get full rule and store it
        Since rules are Streamer specific this method cannot be fully in the storage manager
        :param rules: the matching rules of the collected tweet
        """
        tags = [r.tag for r in rules]
        ids = [r.id for r in rules]
        ids_to_store = self._storages_manager.get_non_existing_rules(ids=ids, tags=tags)
        if ids_to_store:
            if self._config.verbose:
                self._logger.info(f"Storing new rules: {ids_to_store}")
            self._storages_manager.save_rules(self.get_rules(ids=ids_to_store))

    def _handle_user(self, tweet):
        """
        get users in tweet
        check if users in tweet have all their data stored in storage
        if new user then save it, question => save only currently available data or do a get /user to get all data
        :param tweet:
        :return:
        """
        pass

    def _handle_tweet(self, tweet: Tweet):
        self._log_tweets(tweet)
        # make sure rules are already saved
        self._handle_rules(tweet.matching_rules)
        # save user info if there are some:
        self._handle_user(tweet)
        # save tweet and media asynchrounosly
        # TODO: change to a queue to avoid creating a thread everytime
        self.executor.submit(self._save_tweet_data, tweet=tweet)

    def _save_tweet_data(self, tweet: Tweet):
        # get all tags associated to the tweet
        tags = list(set([r.tag for r in tweet.matching_rules]))
        # save media if there are some
        if tweet.includes and tweet.includes.media:
            self._storages_manager.save_media(tweet.includes.media, tweet.data.id, tags)
        self._storages_manager.save_tweets([tweet], tags)

    def _handle_errors(self, errors: List[dict], *args) -> None:
        """
        Some errors might still be wrapped in a 200 response
        So they need to be handle manually and not in Collector._error_handler
        which will only be triggered for responses > 299
        :param errors: a list of errors dictionnary
        :param args: the arguments to pass to collect when retrying
        """
        for error in errors:
            self._logger.error(f"""The following error was encountered: {error}""")
        if errors[0]['title'] in ['Authorization Error', 'Forbidden']:
            # Authorization Error: the tweet is private
            # Forbidden: the user is probably suspended
            # in all those cases we continue to collect, it's not a twitter blocking the connection
            return
        else:
            raise requests.RequestException()

    def collect(self, sub_process: bool = False, fetch_minutes: int = False):
        """
        Main method to collect tweets in a stream
        :param sub_process: should the collect be run in a subprocess ?
        :param fetch_minutes: if you have a pro or an academic account, you can specify
        an int between 1 and 5 to tell the stream to fetch tweets from the past minutes.
        :return:
        """
        super(Streamer, self).collect()
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
        try:
            with self._client.get("tweets/search/stream", params=params, stream=True, timeout=5000) as resp:
                for line in resp.iter_lines():
                    if line:
                        data = json.loads(line.decode("utf-8"))
                        if "errors" in data:
                            self._handle_errors(data['errors'])
                        tweet = Tweet(**data)
                        self._handle_tweet(tweet)
                    else:
                        self._logger.info("waiting for new tweets")
        except requests.RequestException:
            self._retry_count += 1
            if self._retry_count < self._config.max_retries:
                self._logger.error("""The collect will try to start again in 30s""")
                time.sleep(30)
                self.collect(sub_process, fetch_minutes)

