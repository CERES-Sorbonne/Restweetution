from typing import Optional, List, Dict

from pydantic import BaseModel

from restweetution.collectors import Streamer
from restweetution.twitter_client import TwitterClient
from restweetution.models.config.tweet_config import QueryParams
from restweetution.storage.storages.storage import Storage
from restweetution.storage.storage_manager.storage_manager import StorageManager


class MainConfig(BaseModel):
    client: Optional[TwitterClient]
    client_token: Optional[str]

    storages: Dict[str, Storage] = {}
    storage_list: List[Storage] = []

    storage_manager: Optional[StorageManager]
    storage_tags: Optional[dict] = []

    media_download: bool = True
    media_root_dir: str = None

    streamer: Optional[Streamer]
    streamer_rules: Optional[List[dict]]
    streamer_query_params: Optional[QueryParams]
    streamer_verbose: Optional[bool]

    class Config:
        arbitrary_types_allowed = True
