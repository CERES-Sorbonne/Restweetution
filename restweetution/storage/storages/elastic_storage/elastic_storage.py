import asyncio
from typing import List

from elasticsearch import AsyncElasticsearch
from elasticsearch import helpers

from restweetution.models.storage.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.error import ErrorModel
from restweetution.models.storage.twitter import Media
from restweetution.models.storage.twitter import Poll
from restweetution.models.storage.twitter.place import Place
from restweetution.models.storage.twitter.tweet import TweetResponse, User, StreamRule, RestTweet
from restweetution.storage.storages.storage import Storage


class ElasticStorage(Storage):
    def __init__(self, name: str, **kwargs):
        """
        Storage for Elasticsearch stack
        :param name: Name of the storage. Human friendly identifier
        """

        super().__init__(name=name, **kwargs)
        self.rules = {}
        self.es = AsyncElasticsearch(kwargs.get('url'), basic_auth=(kwargs.get('user'), kwargs.get('pwd')))

    def __del__(self):
        asyncio.run(self.es.close())

    async def save_bulk(self, data: BulkData):
        actions = []
        actions.extend(self._rules_to_bulk_actions(list(data.rules.values())))
        actions.extend(self._users_to_bulk_actions(list(data.users.values())))
        actions.extend(self._tweet_to_bulk_actions(list(data.tweets.values())))
        actions.extend(self._media_to_bulk_actions(list(data.medias.values())))
        actions.extend(self._poll_to_bulk_actions(list(data.polls.values())))
        actions.extend(self._place_to_bulk_actions(list(data.places.values())))

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

    @staticmethod
    def _media_to_bulk_actions(medias: List[Media]):
        for media in medias:
            yield {
                "_op_type": 'index',
                "_index": "media",
                "_id": media.media_key,
                "_source": media.dict()
            }

    @staticmethod
    def _place_to_bulk_actions(places: List[Place]):
        for place in places:
            yield {
                "_op_type": 'index',
                "_index": "place",
                "_id": place.id,
                "_source": place.dict()
            }

    @staticmethod
    def _poll_to_bulk_actions(polls: List[Poll]):
        for poll in polls:
            yield {
                "_op_type": 'index',
                "_index": "poll",
                "_id": poll.id,
                "_source": poll.dict()
            }

    @staticmethod
    def _custom_data_to_bulk_actions(datas: List[CustomData]):
        for data in datas:
            yield {
                "_op_type": 'index',
                "_index": ElasticStorage._custom_key(data.key),
                "_id": data.id,
                "_source": data.data
            }

    @staticmethod
    def _custom_key(key: str):
        return 'custom_data_' + key

    async def save_error(self, error: ErrorModel):
        await self.es.index(index='error', document=error.dict())
        await self.es.indices.refresh(index='error')

    async def save_tweet(self, tweet: RestTweet):
        await self.save_tweets([tweet])

    async def save_tweets(self, tweets: List[RestTweet]):
        for tweet in tweets:
            await self.es.index(index="tweet", id=tweet.id, document=tweet.dict())
        await self.es.indices.refresh(index="tweet")

    async def get_tweets(self, ids: List[str] = None, no_ids=None) -> List[TweetResponse]:
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

    async def save_medias(self, medias: List[Media]):
        for media in medias:
            await self.es.index(index="media", id=media.media_key, document=media.dict())
        await self.es.indices.refresh(index="media")

    async def save_custom_datas(self, datas: List[CustomData]):
        await helpers.async_bulk(self.es, self._custom_data_to_bulk_actions(datas))

    async def get_custom_datas(self, key: str) -> List[CustomData]:
        res = []
        async for doc in helpers.async_scan(self.es, index=self._custom_key(key)):
            res.append(doc)
        return [CustomData(key=key, id=d['_id'], data=d['_source']) for d in res]

    async def del_custom_datas(self, key: str):
        await self.es.delete_by_query(index=self._custom_key(key), body={"query": {"match_all": {}}})
