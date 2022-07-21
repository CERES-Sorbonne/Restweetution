from typing import Optional, List

from pydantic import BaseModel

from restweetution.collectors import Streamer
from restweetution.twitter_client import TwitterClient
from restweetution.models.tweet_config import QueryParams
from restweetution.storage.document_storages.document_storage import Storage
from restweetution.storage.storage_manager import StorageManager


class MainConfig(BaseModel):
    client: Optional[TwitterClient]
    client_token: Optional[str]

    storage_manager: Optional[StorageManager]
    storage_tags: Optional[dict] = []
    storages: Optional[List[Storage]] = []
    main_storage: Storage = None

    download_media: bool = False
    media_root_dir: str = None

    streamer: Optional[Streamer]
    streamer_rules: Optional[List[dict]]
    streamer_query_params: Optional[QueryParams]
    streamer_verbose: Optional[bool]

    class Config:
        arbitrary_types_allowed = True
