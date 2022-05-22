import os
from pathlib import Path

from pydantic import BaseModel, Extra, root_validator
from typing import Optional, Union, Callable, List

from restweetution.models.examples_config import BASIC_CONFIG
from restweetution.models.tweet_config import TweetConfig
from restweetution.storage.async_storage import AsyncStorage
from restweetution.storage.storage import Storage


class StorageConfig(BaseModel):
    root: Optional[str]
    max_size: Optional[int] = None
    tags: Optional[List[str]]


class FileStorageConfig(StorageConfig, extra=Extra.forbid):
    root_directory: Optional[str] = os.path.join(str(Path.home()), 'outputTweets')


class SSHFileStorageConfig(StorageConfig, extra=Extra.forbid):
    host: str
    user: str
    password: str
    root: str = os.path.join(str(Path.home()), 'outputTweets')


StorageOrConfig = Union[StorageConfig, AsyncStorage, Storage]


class StreamConfig(BaseModel):
    token: str
    tweets_storages: Optional[List[StorageOrConfig]]
    media_storages: Optional[List[StorageOrConfig]]
    tweet_config: Optional[TweetConfig] = BASIC_CONFIG
    max_retries: Optional[int] = 3
    verbose: Optional[bool] = False
    download_media: Optional[bool] = True
    average_hash: Optional[bool] = False
    custom_handler: Optional[Union[Callable]]

    @root_validator
    def validate_media_storage(cls, values):
        """
        Used to create a media storage if none is provided
        """
        if not values['media_storages'] and values['download_media']:
            raise ValueError("The config is set to download images and videos but no media storage was provided")
        return values

    # allows to use custom classes as types
    class Config:
        arbitrary_types_allowed = True
