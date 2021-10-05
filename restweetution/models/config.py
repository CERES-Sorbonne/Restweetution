import os
from importlib import import_module
from pathlib import Path

from pydantic import BaseModel, Extra, root_validator, validator
from typing import Optional, Union, Callable

from restweetution.models.examples_config import BASIC_CONFIG
from restweetution.models.tweet_config import TweetConfig


class StorageConfig(BaseModel):
    root_directory: Optional[str]
    max_size: Optional[int] = None


class FileStorageConfig(StorageConfig, extra=Extra.forbid):
    root_directory: Optional[str] = os.path.join(str(Path.home()), 'outputTweets')


class SSHFileStorageConfig(StorageConfig, extra=Extra.forbid):
    host: str
    user: str
    password: str
    root_directory: str = os.path.join(str(Path.home()), 'outputTweets')


class Config(BaseModel):
    token: str
    tweet_storage: Optional[Union[FileStorageConfig, SSHFileStorageConfig]] = FileStorageConfig()
    media_storage: Optional[Union[FileStorageConfig, SSHFileStorageConfig]]
    tweet_config: Optional[TweetConfig] = BASIC_CONFIG
    max_retries: Optional[int] = 3
    verbose: Optional[bool] = False
    custom_handler: Optional[Union[Callable]]

    @root_validator
    def validate_media_storage(cls, values):
        if not values['media_storage']:
            # if not media storage, just store at the same place than tweets in folder media
            values['media_storage'] = values['tweet_storage'].copy()
            values['media_storage'].root_directory = os.path.join(values['media_storage'].root_directory, 'media')
        return values
