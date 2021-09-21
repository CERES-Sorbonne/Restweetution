from pydantic import BaseModel
from typing import Optional, Union

from restweetution.models.examples_config import BASIC_CONFIG
from restweetution.models.tweet_config import TweetConfig


class StorageConfig(BaseModel):
    root_directory: Optional[str]
    max_size: Optional[int] = 1000


class FileStorageConfig(StorageConfig):
    root_directory: Optional[str] = "/home/outputTweets"


class SSHFileStorageConfig(StorageConfig):
    host: str
    user: str
    password: str
    root_directory: str = "/home/outputTweets"


class Config(BaseModel):
    token: str
    tweetStorage: Optional[Union[FileStorageConfig, SSHFileStorageConfig]] = FileStorageConfig()
    mediaStorage: Optional[Union[FileStorageConfig, SSHFileStorageConfig]] = FileStorageConfig(root_directory="/home/outputTweets/media")
    tweetConfig: Optional[TweetConfig] = BASIC_CONFIG
