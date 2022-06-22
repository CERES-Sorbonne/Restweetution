import hashlib
import io
import logging
from io import BytesIO
from typing import List, Dict

import imagehash
import httpx as requests
from PIL import Image

from restweetution.models.stream_rule import StreamRule
from restweetution.models.tweet import TweetResponse, Media, RestTweet
from restweetution.models.user import User
from restweetution.storage.async_storage import AsyncStorage
from restweetution.utils import TwitterDownloader


class AsyncStorageManager:
    def __init__(self):
        """
        Utility class to provide a single entry point to a Collector in order to perform all storages operations
        """

        self._tweet_storages: List[AsyncStorage] = []
        self._media_storages: List[AsyncStorage] = []
        self.storage_tags: Dict[str, List[str]] = {}

        # self.media_storages = [self._resolve_storage(s) for s in media_storages]
        self.media_downloader = TwitterDownloader()
        self.logger = logging.getLogger("StorageManager")

        self.average_hash = False

    def __str__(self):
        s = "    Tweets, Users and Rules stored at: \n                "
        for t in self.get_tweet_storages():
            s += "- " + str(t) + "\n                "
        s += "Pictures, Gif and Videos stored at: \n                "
        for m in self.get_media_storages():
            s += "- " + str(m)
        return s

    def add_storage_tags(self, storage: AsyncStorage, tags: List[str]):
        name = storage.name
        for tag in [t for t in tags if t not in self.storage_tags[name]]:
            self.storage_tags[name].append(tag)

    def remove_storage_tags(self, storage: AsyncStorage, tags: List[str]):
        name = storage.name
        if not self.storage_tags[name]:
            return
        self.storage_tags[name] = [s for s in self.storage_tags[name] if s not in tags]

    def add_storage(self, storage: AsyncStorage, tags: List[str] = None):
        if storage.name in [s.name for s in self._tweet_storages]:
            self.logger.warning(f'Storage name must be unique! name: {storage.name} is already taken')
            return
        self._tweet_storages.append(storage)
        self.storage_tags[storage.name] = []

        if tags:
            self.add_storage_tags(storage, tags)

    def remove_storages(self, names: List[str] = None):
        to_delete = self._tweet_storages
        if names:
            to_delete = [s.name for s in to_delete if s.name in names]

        for name in to_delete:
            self.storage_tags.pop(name)

        self._tweet_storages = [s for s in self._tweet_storages if s.name not in to_delete]

    async def save_tweet(self, tweet: RestTweet, tags: List[str] = None):
        for s in self.get_tweet_storages_by_tags(tags):
            await s.save_tweet(tweet)

    def has_tags(self, storage: AsyncStorage, tags):
        """
        Test if the given storage has at least one of the tags
        """
        shared = [t for t in self.storage_tags[storage.name] if t in tags]
        return len(shared) > 0

    def get_storages_by_tags(self, tags: List[str]):
        storages = self._tweet_storages
        storages = [s for s in storages if self.has_tags(s, tags)]
        return storages

    def get_tweet_storages(self):
        return self._tweet_storages

    def get_tweet_storages_by_tags(self, tags: List[str]):
        # get tweet storages
        storages = self.get_tweet_storages()
        storages = [s for s in storages if self.has_tags(s, tags)]
        return storages

    def get_media_storages(self):
        return self._media_storages

    def get_media_storages_by_tags(self, tags):
        storages = self.get_media_storages()
        storages = [s for s in storages if self.has_tags(s, tags)]
        return storages

    # async def get_tweets(self, tags: List[str] = None, ids: List[str] = None, duplicate: bool = False) -> Iterator[
    #     TweetResponse]:
    #     storages = [self.tweets_storages[0]] if not duplicate else self.tweets_storages
    #     for s in storages:
    #         for r in await s.get_tweets(tags=tags, ids=ids):
    #             yield r

    def bulk_save(self, bulk_data, tags: List[str]):
        for s in self.get_storages_by_tags(tags):
            s.buffered_bulk_save(bulk_data)

    async def save_rules(self, rules: List[StreamRule]):
        """
       Persist a list of rules if not existing
       :param rules: list of rules
       :return: none
        """
        tags = [r.tag for r in rules]
        for s in self.get_tweet_storages_by_tags(tags):
            await s.save_rules(rules)

    async def save_users(self, users: List[User], tags: List[str]):
        for s in self.get_tweet_storages_by_tags(tags):
            await s.save_users(users)

    async def save_media(self, media_list: List[Media], tweet_id: str, tags: List[str] = None) -> None:
        # first check if we have any valid tags, otherwise there is no point of downloading the media
        valid_storages = self.get_media_storages_by_tags(tags)
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
                await s.save_media(full_name, io.BytesIO(buffer))
            for s in self.get_tweet_storages_by_tags(tags):
                await s.save_media_link(media.media_key, signature, average_hash)

    @staticmethod
    def _get_file_type(file_type: str) -> str:
        if file_type == "video":
            return "mp4"
        elif file_type == "photo":
            return "jpeg"
        else:
            # store gif files as mp4 because it's the way there are downloaded
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
