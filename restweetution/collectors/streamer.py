import json
import os
import time
from typing import Union, List

from restweetution.collectors.collector import Collector
from restweetution.models.tweet import Tweet, Rule


class Streamer(Collector):
    def __init__(self, config: Union[dict, str]):
        super(Streamer, self).__init__(config)
        self._fetch_minutes = False

    def get_rules(self) -> list[dict]:
        """
        Return the list of rules defined to collect tweets during a stream
        :return: the list of rules
        """
        res = self._client.get("tweets/search/stream/rules")
        return res.json().get('data', [])

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
            raise ValueError(f"The following errors happened while trying to create "
                             f"the rule: {res.json()['errors'][0]['details']}")
        else:
            return res.json()['data'][0]['id']

    def remove_rule(self, id_to_remove: str) -> None:
        """
        Remove a rule
        :param id_to_remove: the id of the rule to remove
        :return: None
        """
        res = self._client.post("tweets/search/stream/rules", json={
            "delete": {
                "ids": [id_to_remove]
            }

        })
        if "errors" in res.json():
            raise ValueError(f"The following errors happened while trying to delete "
                             f"the rule: {res.json()['errors'][0]['errors']['message']}")

    def _log_tweets(self, tweet: Tweet):
        self.tweets_count += 1
        if self._config.verbose:
            self._logger.info(tweet.data.text)
        if self.tweets_count % 10 == 0:
            self._logger.info(f'{self.tweets_count} tweets collected')

    def _handle_rules(self, rules: List[Rule]) -> None:
        for rule in rules:
            self.get_rules()

    def handle_tweet(self, tweet: Tweet):
        self._log_tweets(tweet)
        # make sure rules are already saved
        self._handle_rules(tweet.matching_rules)
        # save user info if there are some:
        self._handle_user(tweet)
        # save media if there are some
        self._handle_media(tweet)
        # get all tags associated to the tweet
        tags = list(set([r.tag for r in tweet.matching_rules]))
        self._storage_manager.save_tweets([tweet], tags)

    def _handle_errors(self, errors: List[dict], *args) -> None:
        """
        Some errors might still be wrapped in a 200 response
        So they need to be handle manually and not in Collector._error_handler
        which will only be triggered for responses > 299
        :param errors: a list of errors dictionnary
        :param args: the arguments to pass to collect when retrying
        :return: none
        """
        for error in errors:
            self._logger.error(f"""The following error was encountered: {error}""")
        if self._retry_count < self._config.max_retries:
            self._logger.error("""The collect will try to start again in 30s""")
            time.sleep(30)
            self.collect(*args)

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
        if len(self.get_rules()) == 0:
            self._logger.warning("Stream started but no rules are configured currently, use add_rule to add a new_rule")
        params = self._create_params_from_config()
        if self._fetch_minutes:
            params = {**params, 'backfill_minutes': self._fetch_minutes}
        with self._client.get("tweets/search/stream", params=params, stream=True, timeout=5000) as resp:
            for line in resp.iter_lines():
                if line and self._has_free_space():
                    data = json.loads(line.decode("utf-8"))
                    if "errors" in data:
                        self._handle_errors(data['errors'], sub_process, fetch_minutes)
                    tweet = Tweet(**data)
                    self.handle_tweet(tweet)
                else:
                    self._logger.info("waiting for new tweets")
