import io
from typing import List

from elasticsearch import helpers

from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter.media import Media
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.poll import Poll
from restweetution.models.twitter.tweet import TweetResponse, User, StreamRule, RestTweet
from restweetution.storage.document_storages.document_storage import Storage
from elasticsearch import AsyncElasticsearch


class ElasticTweetStorage(Storage):
    def __init__(self, name: str, **kwargs):
        """
        Storage for Elasticsearch stack
        :param name: Name of the storage. Human friendly identifier
        """

        super().__init__(name=name, **kwargs)
        self.rules = {}
        self.es = AsyncElasticsearch(kwargs.get('url'), basic_auth=(kwargs.get('user'), kwargs.get('pwd')))

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

    async def save_error(self, error: any):
        await self.es.index(index='error', document=error)
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
