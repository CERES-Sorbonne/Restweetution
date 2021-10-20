import hashlib
import io
import logging
from io import BytesIO
from typing import List, Iterator, Dict

import imagehash
import requests
from PIL import Image

from restweetution.models.config import StorageConfig, FileStorageConfig, SSHFileStorageConfig
from restweetution.models.tweet import Tweet, Rule, StreamRule, Media
from restweetution.storage.object_storage.filestorage import FileStorage, SSHFileStorage
from restweetution.storage.object_storage.object_storage_wrapper import ObjectStorageWrapper
from restweetution.storage.storage_wrapper import StorageWrapper
from restweetution.utils import TwitterDownloader


class StorageManager:
    def __init__(self, tweets_storages: List[StorageConfig], media_storages:List[StorageConfig], partial_hash: bool = True):
        """
        Utility class to provide a single entry point to a Collector in order to perform all storages operations
        :param tweets_storages:
        :param media_storages:
        :param partial_hash:
        """
        self.tweets_storages = [self._resolve_storage(s) for s in tweets_storages]
        self.media_storages = [self._resolve_storage(s, media=True) for s in media_storages]
        self.partial_hash = partial_hash
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

    def save_tweets(self, tweets: List[Tweet], tags: List[str] = None):
        # save collected tweet in every tag folder
        errors = 0
        for s in self.tweets_storages:
            if s.has_free_space:
                s.save_tweets(tweets, tags)
            else:
                errors += 1
                self.logger.warning(f"Maximum size reached for storage {str(s)}")
        if errors == len(self.tweets_storages):
            raise OSError("The maxsize of the storage directory has been reached")

    def get_tweets(self, tags: List[str] = None, ids: List[str] = None, duplicate: bool = False) -> Iterator[Tweet]:
        storages = [self.tweets_storages[0]] if not duplicate else self.tweets_storages
        for s in storages:
            for r in s.get_tweets(tags=tags, ids=ids):
                yield r

    def save_rules(self, rules: List[Rule]):
        """
       Persist a list of rules if not existing
       :param rules: list of rules
       :return: none
        """
        for s in self.tweets_storages:
            s.save_rules(rules)

    def get_rules(self, ids: List[str] = None, duplicate: bool = False) -> Iterator[StreamRule]:
        """
        Returns an iterator on the rules of the stream
        :param ids:
        :param duplicate:
        :return:
        """
        storages = [self.tweets_storages[0]] if not duplicate else self.tweets_storages
        for s in storages:
            for r in s.get_rules(ids):
                yield r

    def get_rules_ids(self) -> List[str]:
        return [r.id for r in self.get_rules()]

    def save_users(self):
        pass

    def save_media(self, media_list: List[Media], tweet_id: str) -> Dict[str, Dict[str, str]]:
        stored_media = self.media_storages[0].list_dir()
        uris = {}
        for media in media_list:
            media_type = media.url.split('.')[-1] if media.url else self._get_file_type(media.type)
            full_name = f"{media.media_key}.{media_type}"
            # check if it was already downloaded:
            if full_name in stored_media:
                logging.info("This image was already downloaded")
            # if it's an image
            if media.url:
                try:
                    logging.info(f"Downloading {media.url} with id: {media.media_key} and tweet_id: {tweet_id}")
                    res = requests.get(media.url)
                    buffer: bytes = res.content
                    signature = self._compute_signature(buffer)
                except requests.HTTPError as e:
                    self.logger.warning(f"There was an error downloading image {media.url}: " + str(e))
                    continue
            # TODO: change this when v2 api supports url for video and gifs
            else:  # then it's a video or a gif
                buffer: bytes = self.media_downloader.download(tweet_id=tweet_id, media_type=media.type)
                signature = self._compute_signature(buffer=buffer, image=False)

            uris[media.media_key] = {}

            for s in self.media_storages:
                uri = s.save_media(full_name, io.BytesIO(buffer), signature)
                # save the returned uri in a dict
                uris[media.media_key][s.name] = uri
            # add the newly stored image to the list of media
            stored_media.append(full_name)
        return uris

    @staticmethod
    def _get_file_type(file_type: str) -> str:
        if file_type == "video":
            return "mp4"
        elif file_type == "photo":
            return "jpeg"
        else:
            return "gif"

    def get_media(self, tweet: Tweet):
        pass

    def _save_video(self, media: Media, tweet_id: str) -> bytes:
        return b""

    def _compute_signature(self, buffer: bytes, image: bool = True):
        if self.partial_hash and image:
            img = Image.open(BytesIO(buffer))
            return str(imagehash.average_hash(img))
        else:
            return hashlib.sha1(buffer).hexdigest()

    @staticmethod
    def _resolve_storage(config: StorageConfig, media: bool = False) -> StorageWrapper:
        """
        Utility method that takes a StorageConfig as input and returns a wrapped storage
        :param config: the storage config
        :return: a storage wrapper, which means a storage that exposes all methods to save or get data
        """
        if isinstance(config, FileStorageConfig):
            return ObjectStorageWrapper(FileStorage(config), media)
        elif isinstance(config, SSHFileStorageConfig):
            return ObjectStorageWrapper(SSHFileStorage(config), media)
        else:
            raise ValueError(f"Unhandled type of storage: {type(config)}")

