import concurrent.futures
import json
import time
from typing import Union, List

import requests

from restweetution.collectors.collector import Collector
from restweetution.models.tweet import Tweet, Rule, StreamRule


class Streamer(Collector):
    def __init__(self, config: Union[dict, str]):
        super(Streamer, self).__init__(config)
        self._fetch_minutes = False
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def get_rules(self, ids: List[str] = None) -> List[StreamRule]:
        """
        Return the list of rules defined to collect tweets during a stream
        :param ids: an optional list of ids to fetch only specific rules
        :return: the list of rules
        """
        uri = "tweets/search/stream/rules"
        if ids:
            uri += f"?ids={','.join(ids)}"
        res = self._client.get(uri)
        return [StreamRule(**r) for r in res.json().get('data', [])]

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

    def remove_rule(self, id_to_remove: str) -> None:
        """
        Remove a rule
        :param id_to_remove: the id of the rule to remove
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
            self._logger.info('\n'.join([f'{r.value}, tag: {r.tag}' for r in rules]))
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

