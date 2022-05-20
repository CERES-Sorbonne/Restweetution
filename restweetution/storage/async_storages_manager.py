import hashlib
import io
import logging
from io import BytesIO
from typing import List, Iterator

import imagehash
import requests
from PIL import Image

from restweetution.models.config import StorageConfig, StorageOrConfig
from restweetution.models.tweet import TweetResponse, RuleLink, StreamRule, Media, RestTweet
from restweetution.storage.async_storage import AsyncStorage
from restweetution.storage.elastic_storage.elastic_storage import ElasticStorage
from restweetution.utils import TwitterDownloader


class AsyncStoragesManager:
    def __init__(self, tweets_storages: List[StorageOrConfig], media_storages: List[StorageOrConfig],
                 average_hash: bool = False, download_media: bool = True):
        """
        Utility class to provide a single entry point to a Collector in order to perform all storages operations
        :param tweets_storages: list of tweets storages
        :param media_storages: list of media storages
        :param average_hash: should we also compute average hash to find similar images ?
        :param download_media: should we download images and videos ?
        """
        self.tweets_storages = [self._resolve_storage(s) for s in tweets_storages]
        self.media_storages = [self._resolve_storage(s) for s in media_storages]
        self.average_hash = average_hash
        self.download_media = download_media
        self.media_downloader = TwitterDownloader()
        self.logger = logging.getLogger("Storage")

    def __str__(self):
        s = "    Tweets, Users and Rules stored at: \n                "
        for t in self.tweets_storages:
            s += "- " + str(t) + "\n                "
        s += "Pictures, Gif and Videos stored at: \n                "
        for m in self.media_storages:
            s += "- " + str(m)
        return s

    async def save_tweets(self, tweets: List[RestTweet], tags: List[str] = None):
        # save collected tweets
        size_errors = 0
        tags_errors = 0
        for s in self.tweets_storages:
            if s.has_free_space:
                if s.valid_tags(tags):
                    await s.save_tweets(tweets, tags)
                else:
                    tags_errors += 1
            else:
                size_errors += 1
                self.logger.warning(f"Maximum size reached for storage {str(s)}")
        if size_errors == len(self.tweets_storages):
            raise OSError("The maxsize of the storage directory has been reached on every storage")
        if tags_errors == len(self.tweets_storages):
            raise ValueError(f"No storage was configured to handle data with tags: {tags}")

    async def get_tweets(self, tags: List[str] = None, ids: List[str] = None, duplicate: bool = False) -> Iterator[
        TweetResponse]:
        storages = [self.tweets_storages[0]] if not duplicate else self.tweets_storages
        for s in storages:
            for r in await s.get_tweets(tags=tags, ids=ids):
                yield r

    async def save_rules(self, rules: List[RuleLink]):
        """
       Persist a list of rules if not existing
       :param rules: list of rules
       :return: none
        """
        tags = [r.tag for r in rules]
        for s in self.tweets_storages:
            if s.valid_tags(tags):
                await s.save_rules(rules)

    def get_non_existing_rules(self, ids: List[str], tags: List[str] = None):
        """
        Return the ids of the rules that are not saved in concerned storages
        :param ids: ids of the rules to filter
        :param tags: tags of the rules to filer
        :return: the filtered list of ids
        """
        all_ids = []
        for s in self.tweets_storages:
            # if the rules should be saved for this storage
            if s.valid_tags(tags):
                # keep only ids that were not saved already
                already_saved = [r.id for r in s.get_rules()]
                all_ids = [*all_ids, *[_id for _id in ids if _id not in already_saved]]
        return all_ids

    def get_rules(self, ids: List[str] = None, tags: List[str] = None) -> Iterator[StreamRule]:
        """
        Returns an iterator on the rules of the stream
        :param ids: get some specific rules
        :param tags: get some specific tags
        :return:
        """
        for s in self.tweets_storages:
            if s.valid_tags(tags):
                for r in s.get_rules(ids):
                    yield r

    def get_rules_ids(self, tags: List[str] = None) -> List[str]:
        return [r.id for r in self.get_rules(tags=tags)]

    def save_users(self):
        pass

    async def save_media(self, media_list: List[Media], tweet_id: str, tags: List[str] = None) -> None:
        # first check if we have any valid tags, otherwise there is no point of downloading the media
        valid_storages = []
        for s in self.media_storages:
            if s.valid_tags(tags):
                valid_storages.append(s)
        if len(valid_storages) == 0:
            return

        if not self.save_media:
            return

        # download media
        average_hash = None
        for media in media_list:
            media_type = media.url.split('.')[-1] if media.url else self._get_file_type(media.type)
            # if it's an image
            if media.url:
                try:
                    logging.info(f"Downloading {media.url} with id: {media.media_key} and tweet_id: {tweet_id}")
                    # TODO: make async
                    res = requests.get(media.url)
                    buffer: bytes = res.content
                    if self.average_hash:
                        average_hash = self._computer_average_signature(buffer)
                except requests.HTTPError as e:
                    self.logger.warning(f"There was an error downloading image {media.url}: " + str(e))
                    continue
            # TODO: change this when v2 api supports url for video and gifs
            else:  # then it's a video or a gif
                # TODO: make async
                buffer: bytes = self.media_downloader.download(tweet_id=tweet_id, media_type=media.type)

            signature = self._compute_signature(buffer)
            if media_type == 'gif':
                # save gif as mp4 for size issue
                media_type = 'mp4'
            full_name = f"{signature}.{media_type}"

            for s in valid_storages:
                # TODO: make async
                await s.save_media(full_name, io.BytesIO(buffer))
            for s in self.tweets_storages:
                if s.valid_tags(tags):
                    # TODO: make async
                    s.save_media_link(media.media_key, signature, average_hash)

    @staticmethod
    def _get_file_type(file_type: str) -> str:
        if file_type == "video":
            return "mp4"
        elif file_type == "photo":
            return "jpeg"
        else:
            # store gif files as mp4 cause it's the way there are downloaded
            return "gif"

    def get_media(self, tweet: TweetResponse):
        pass

    @staticmethod
    def _compute_signature(buffer: bytes):
        return hashlib.sha1(buffer).hexdigest()

    @staticmethod
    def _computer_average_signature(buffer: bytes):
        img = Image.open(BytesIO(buffer))
        return str(imagehash.average_hash(img))

    @staticmethod
    def _storage_from_config(config: StorageConfig):
        """
        Utility method that takes a StorageConfig as input and returns a storage
        :param config: the storage config
        """
        # if isinstance(config, FileStorageConfig):
        #     return FileStorage(**config.dict())
        # elif isinstance(config, SSHFileStorageConfig):
        #     return SSHStorage(**config.dict())
        if isinstance(config, ElasticStorage):
            return ElasticStorage(**config.dict())
        else:
            raise ValueError(f"Unhandled type of storage: {type(config)}")

    def _resolve_storage(self, storage_or_config: StorageOrConfig) -> AsyncStorage:
        """
        Utility method to initialize a storage from a Storage Object or a StorageConfig
        :param storage_or_config: a Object containing a Storage or a StorageConfig, and a list of tags associated
        :return: a storage wrapper, which means a storage that exposes all methods to save or get data
        """
        if isinstance(storage_or_config, StorageConfig):
            storage = self._storage_from_config(storage_or_config)
        else:
            storage = storage_or_config
        return storage
