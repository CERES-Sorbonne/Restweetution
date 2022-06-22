import io
import time
from typing import List, Dict, Union

from elasticsearch import helpers

from restweetution.models.bulk_data import BulkData
from restweetution.models.tweet import TweetResponse, User, StreamRule, RestTweet
from restweetution.storage.async_storage import AsyncStorage
from elasticsearch import AsyncElasticsearch


class ElasticTweetStorage(AsyncStorage):
    def __init__(self,
                 name: str,
                 es_url: str,
                 es_user: str = "",
                 es_pwd: str = ""):
        """
        Storage for Elasticsearch stack
        :param name: Name of the storage. Human friendly identifier
        :param es_config: Connection configuration. Dictionary has 3 fields: url, user, pwd
        """

        super().__init__(name=name)
        self.rules = {}
        self.es = AsyncElasticsearch(es_url, basic_auth=(es_user, es_pwd))

    async def bulk_save(self, data: BulkData):
        actions = []
        actions.extend(self._rules_to_bulk_actions(data.rules))
        actions.extend(self._users_to_bulk_actions(data.users))
        actions.extend(self._tweet_to_bulk_actions(data.tweets))

        await helpers.async_bulk(self.es, actions)

    @staticmethod
    def _rules_to_bulk_actions(rules: List[StreamRule]):
        for rule in rules:
            yield {
                "_op_type": 'index',
                "_index": "rule",
                "_id": rule.id,
                "_doc": rule.dict()
            }

    @staticmethod
    def _users_to_bulk_actions(users: List[User]):
        for user in users:
            yield {
                "_op_type": 'index',
                "_index": "user",
                "_id": user.id,
                "_doc": user.dict()
            }

    @staticmethod
    def _tweet_to_bulk_actions(tweets: List[RestTweet]):
        for tweet in tweets:
            yield {
                "_op_type": 'index',
                "_index": "tweet",
                "_id": tweet.id,
                "_source": tweet.dict()
            }

    async def save_tweet(self, tweet: RestTweet):
        await self.save_tweets([tweet])

    async def save_tweets(self, tweets: List[RestTweet]):
        for tweet in tweets:
            await self.es.index(index="tweet", id=tweet.id, document=tweet.dict())
        await self.es.indices.refresh(index="tweet")

    async def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> List[TweetResponse]:
        pass

    async def save_rule(self, rule: StreamRule):
        await self.save_rules([rule])

    async def save_rules(self, rules: List[StreamRule]):
        to_save = [r for r in rules if r.id not in self.rules]
        if not to_save:
            return

        for r in to_save:
            self.rules[r.id] = True
            await self.es.index(index="rule", id=r.id, document=r.dict())
        await self.es.indices.refresh(index="rule")

    async def save_users(self, users: List[User]):
        for user in users:
            await self.es.index(index="user", id=user.id, document=user.dict())
        await self.es.indices.refresh(index="user")

    def save_media(self, file_name: str, buffer: io.BufferedIOBase) -> str:
        """
        Save a buffer to the storage and returns an uri to the stored file
        :param file_name: the signature of the media with the file_type
        :param buffer: the buffer to store
        :return: an uri to the resource created
        """
        pass

    def get_media(self, media_key) -> io.BufferedIOBase:
        pass

    def list_dir(self) -> List[str]:
        pass

    def has_free_space(self) -> bool:
        return True

    def save_media_link(self, media_key, signature, average_signature):
        """
        Save the match between the media_key and the computed signature of the media
        """
        pass
