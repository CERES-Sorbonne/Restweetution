from typing import Optional, List, Any

from pydantic import BaseModel

from restweetution.collectors import AsyncStreamer
from restweetution.storage.async_storage import AsyncStorage
from restweetution.storage.async_storage_manager import AsyncStorageManager


class MainConfig(BaseModel):
    client: Optional[Any]
    storage_tags: Optional[dict] = []
    tweet_storages: Optional[List[AsyncStorage]] = []
    storage_manager: Optional[AsyncStorageManager]
    streamer: Optional[AsyncStreamer]

    class Config:
        arbitrary_types_allowed = True


