from typing import Optional, List

from pydantic import BaseModel

from restweetution.collectors import AsyncStreamer
from restweetution.collectors.async_client import AsyncClient
from restweetution.models.tweet_config import QueryParams
from restweetution.storage.async_storage import AsyncStorage
from restweetution.storage.async_storage_manager import AsyncStorageManager


class MainConfig(BaseModel):
    client: Optional[AsyncClient]
    client_token: Optional[str]

    storage_manager: Optional[AsyncStorageManager]
    storage_tags: Optional[dict] = []
    storage_tweet_storages: Optional[List[AsyncStorage]] = []

    streamer: Optional[AsyncStreamer]
    streamer_rules: Optional[List[dict]]
    streamer_query_params: Optional[QueryParams]
    streamer_verbose: Optional[bool]

    class Config:
        arbitrary_types_allowed = True
