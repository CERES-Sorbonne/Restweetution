import json
import os
from typing import Union

from restweetution.collectors.collector import Collector
from restweetution.models.tweet import Tweet


class Streamer(Collector):
    def __init__(self, config: Union[dict, str]):
        super(Streamer, self).__init__(config)

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

    def handle_tweet(self, tweet: Tweet):
        # save media if there are some
        self._handle_media(Tweet)
        # get all tags associated to the tweet
        tags = list(set([r.tag for r in tweet.matching_rules]))
        # save collected tweet in every tag folder
        for tag in tags:
            path = os.path.join(tag, f"{tweet.data.id}.json")
            self._tweet_storage.put(tweet.json(exlude_none=True, ensure_ascii=False), path)

    def collect(self, sub_process=False, fetch_minutes=False):
        super(Streamer, self).collect()
        # check if some rules are configured
        if len(self.get_rules()) == 0:
            self.__logger.warning("Stream started but no rules are configured currently, use add_rule to add a new_rule")
        with self._client.get("tweets/search/stream", params=self._create_params_from_config(), stream=True, timeout=5000) as resp:
            for line in resp.iter_lines():
                if line and self._has_free_space():
                    data = Tweet(**json.loads(line.decode("utf-8")))
                    self.handle_tweet(data)
                else:
                    self.__logger.info("waiting for new tweets")
