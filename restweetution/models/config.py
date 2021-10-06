import os
from copy import deepcopy
from pathlib import Path

from pydantic import BaseModel, Extra, root_validator
from typing import Optional, Union, Callable, List

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
    tweets_storage: Optional[List[Union[FileStorageConfig, SSHFileStorageConfig]]] = [FileStorageConfig()]
    media_storage: Optional[List[Union[FileStorageConfig, SSHFileStorageConfig]]]
    tweet_config: Optional[TweetConfig] = BASIC_CONFIG
    max_retries: Optional[int] = 3
    verbose: Optional[bool] = False
    custom_handler: Optional[Union[Callable]]

    @root_validator
    def validate_media_storage(cls, values):
        """
        Used to create a media storage if none is provided
        """
        if not values['media_storage']:
            # if not media storage, just store at the same place than tweets in folder media
            values['media_storage'] = deepcopy(values['tweets_storage'])
            for m in values['media_storage']:
                m.root_directory = os.path.join(m.root_directory, 'media')
        return values
