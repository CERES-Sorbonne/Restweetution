import asyncio
import logging
from typing import List

from elasticsearch import AsyncElasticsearch
from elasticsearch import helpers

from restweetution.models.bulk_data import BulkData
from restweetution.models.rule import Rule
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.error import ErrorModel
from restweetution.models.twitter import Media
from restweetution.models.twitter import Poll
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.tweet import TweetResponse, User, Tweet
from restweetution.storages.elastic_storage.bulk_actions import SaveAction, UpdateAction
from restweetution.storages.storage import Storage

es_logger = logging.getLogger('elastic_transport')
es_logger.setLevel(logging.WARNING)

STORAGE_PREFIX = 'storage_'
MEDIA_INDEX = STORAGE_PREFIX + 'media'
PLACE_INDEX = STORAGE_PREFIX + 'place'
POLL_INDEX = STORAGE_PREFIX + 'poll'
TWEET_INDEX = STORAGE_PREFIX + 'tweet'
USER_INDEX = STORAGE_PREFIX + 'user'
RULE_INDEX = STORAGE_PREFIX + 'rule'


def CUSTOM_INDEX(key):
    return 'custom_data_' + key


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
        actions.extend(self._custom_data_to_bulk_actions(list(data.custom_datas.values())))

        await helpers.async_bulk(self.es, actions)

    # Private

    @staticmethod
    def _rules_to_bulk_actions(rules: List[Rule]):
        for rule in rules:
            yield SaveAction(index=RULE_INDEX, id_=rule.id, doc=rule.dict())

    @staticmethod
    def _users_to_bulk_actions(users: List[User]):
        for user in users:
            yield SaveAction(index=USER_INDEX, id_=user.id, doc=user.dict())

    @staticmethod
    def _tweet_to_bulk_actions(tweets: List[Tweet]):
        for tweet in tweets:
            yield SaveAction(index=TWEET_INDEX, id_=tweet.id, doc=tweet.dict())

    @staticmethod
    def _media_to_bulk_actions(medias: List[Media]):
        for media in medias:
            yield SaveAction(index=MEDIA_INDEX, id_=media.media_key, doc=media.dict())

    @staticmethod
    def _place_to_bulk_actions(places: List[Place]):
        for place in places:
            yield SaveAction(index=PLACE_INDEX, id_=place.id, doc=place.dict())

    @staticmethod
    def _poll_to_bulk_actions(polls: List[Poll]):
        for poll in polls:
            yield SaveAction(index=POLL_INDEX, id_=poll.id, doc=poll.dict())

    @staticmethod
    def _custom_data_to_bulk_actions(datas: List[CustomData]):
        for data in datas:
            yield SaveAction(index=CUSTOM_INDEX(data.key), id_=data.id, doc=data.data)

    async def save_error(self, error: ErrorModel):
        await self.es.index(index='error', document=error.dict())
        await self.es.indices.refresh(index='error')

    async def save_tweet(self, tweet: Tweet):
        await self.save_tweets([tweet])

    async def save_tweets(self, tweets: List[Tweet]):
        for tweet in tweets:
            await self.es.index(index="tweet", id=tweet.id, document=tweet.dict())
        await self.es.indices.refresh(index="tweet")

    async def get_tweets(self, ids: List[str] = None, no_ids=None) -> List[TweetResponse]:
        pass

    async def save_rule(self, rule: Rule):
        await self.save_rules([rule])

    async def save_rules(self, rules: List[Rule]):
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
        docs = await self._get_documents(CUSTOM_INDEX(key))
        return [CustomData(key=key, id=d['_id'], data=d['_source']) for d in docs]

    async def get_medias(self, **kwargs) -> List[Media]:
        docs = await self._get_documents(MEDIA_INDEX)
        return [Media(**d['_source']) for d in docs]

    async def update_medias(self, medias: List[Media], delete: List[str] = None):
        await self._bulk(self._media_update_actions(medias, delete))

    async def del_custom_datas(self, key: str):
        await self.es.delete_by_query(index=CUSTOM_INDEX(key),
                                      body={"query": {"match_all": {}}})

    async def _get_documents(self, index: str):
        return [doc async for doc in helpers.async_scan(self.es, index=index, size=10000)]

    @staticmethod
    def _media_update_actions(medias: List[Media], delete: List[str] = None):
        for media in medias:
            yield UpdateAction(index=MEDIA_INDEX, id_=media.media_key, doc=media.dict(), delete=delete)

    async def _bulk(self, actions):
        await helpers.async_bulk(self.es, actions)
