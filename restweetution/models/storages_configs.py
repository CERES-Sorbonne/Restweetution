import os
from pathlib import Path
from typing import Optional, List, Union

from pydantic import BaseModel, Extra

from restweetution.storage.async_storage import AsyncStorage
from restweetution.storage.storage import Storage


class StorageConfig(BaseModel):
    tags: Optional[List[str]]


class ObjectStorageConfig(StorageConfig):
    root: Optional[str]
    max_size = Optional[int] = None


class FileStorageConfig(ObjectStorageConfig, extra=Extra.forbid):
    root: Optional[str] = os.path.join(str(Path.home()), 'outputTweets')


class SSHFileStorageConfig(ObjectStorageConfig, extra=Extra.forbid):
    host: str
    user: str
    password: str
    root: str = os.path.join(str(Path.home()), 'outputTweets')


class ElasticStorageConfig(StorageConfig):
    host: str
    user: str
    password: str


StorageOrConfig = Union[StorageConfig, AsyncStorage, Storage]