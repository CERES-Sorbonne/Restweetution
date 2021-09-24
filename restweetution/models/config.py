from pydantic import BaseModel
from typing import Optional, Union

from restweetution.models.examples_config import BASIC_CONFIG
from restweetution.models.tweet_config import TweetConfig


class StorageConfig(BaseModel):
    root_directory: Optional[str]
    max_size: Optional[int] = None


class FileStorageConfig(StorageConfig):
    root_directory: Optional[str] = "/home/outputTweets"


class SSHFileStorageConfig(StorageConfig):
    host: str
    user: str
    password: str
    root_directory: str = "/home/outputTweets"


class Config(BaseModel):
    token: str
    tweet_storage: Optional[Union[FileStorageConfig, SSHFileStorageConfig]] = FileStorageConfig()
    media_storage: Optional[Union[FileStorageConfig, SSHFileStorageConfig]] = FileStorageConfig(root_directory="/home/outputTweets/media")
    tweet_config: Optional[TweetConfig] = BASIC_CONFIG
    max_retries: Optional[int] = 3
    verbose: Optional[bool] = False
