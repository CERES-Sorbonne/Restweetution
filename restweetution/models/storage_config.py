import os
from pathlib import Path
from typing import Optional, List, Union

from pydantic import BaseModel, Extra

from restweetution.storage.async_storage import AsyncStorage
from restweetution.storage.storage import Storage


class StorageConfig(BaseModel):
    tags: List[str]
    storage: Union[object, dict]


class OsStorageConfig(BaseModel):
    root: Optional[str]
    max_size: Optional[int] = None
    tags: Optional[List[str]]


class FileStorageConfig(OsStorageConfig, extra=Extra.forbid):
    root_directory: Optional[str] = os.path.join(str(Path.home()), 'outputTweets')


class SSHFileStorageConfig(OsStorageConfig, extra=Extra.forbid):
    host: str
    user: str
    password: str
    root: str = os.path.join(str(Path.home()), 'outputTweets')


StorageOrConfig = Union[OsStorageConfig, AsyncStorage, Storage]
