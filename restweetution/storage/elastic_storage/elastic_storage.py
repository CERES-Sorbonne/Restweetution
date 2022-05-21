import io
from typing import List, Iterator
from restweetution.models.tweet import TweetResponse, RuleRef, User, StreamRule, RestTweet
from restweetution.storage.async_storage import AsyncStorage
from elasticsearch import AsyncElasticsearch


class ElasticStorage(AsyncStorage):
    def __init__(self, tags: List[str] = None):
        """
        Storage for Elasticsearch stack
        :param tags: the list of tags that will be saved by this storage
        """
        super().__init__(tags=tags)
        self.rules = []
        self.es = AsyncElasticsearch(
            "https://ceres.huma-num.fr:443/elastic",
            basic_auth=("elastic", "vjD+mlOWmu6=oESqbxSb")
        )

    async def save_tweet(self, tweet: RestTweet, data={}):

        if "matching_rules" in data:
            tweet.matching_rules = data["matching_rules"]

        await self.es.index(index="tweet", id=tweet.id, document=tweet.dict())
        await self.es.indices.refresh(index="tweet")

    async def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> List[TweetResponse]:
        pass

    async def save_rule(self, rule: StreamRule, data={}):
        await self.es.index(index="rule", id=rule.id, document=rule.dict())
        await self.es.indices.refresh(index="rule")

    # async def save_rules(self, rules: List[RuleRef]):
    #     """
    #     Persist a list of rules if not existing
    #     :param rules: list of rules
    #     :return: none
    #     """
    #     self.rules = rules

    def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        return self.rules

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
