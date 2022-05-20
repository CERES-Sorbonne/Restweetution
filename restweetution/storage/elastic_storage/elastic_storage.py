import io
from typing import List, Iterator
from restweetution.models.tweet import TweetResponse, RuleLink, User, StreamRule, RestTweet
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

    async def save_tweets(self, tweets: List[RestTweet], tags: List[str] = None):
        for tweet in tweets:
            await self.es.index(index="tweet", id=tweet.id, document=tweet.dict())
        await self.es.indices.refresh(index="tweet")

    async def get_tweets(self, tags: List[str] = None, ids: List[str] = None) -> List[TweetResponse]:
        pass

    async def save_rules(self, rules: List[RuleLink]):
        """
        Persist a list of rules if not existing
        :param rules: list of rules
        :return: none
        """
        self.rules = rules

    def get_rules(self, ids: List[str] = None) -> Iterator[StreamRule]:
        return self.rules

    def save_users(self, users: List[User]):
        pass

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
