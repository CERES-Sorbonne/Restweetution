from typing import Optional, List, Dict

from pydantic import BaseModel
from tweepy import StreamRule

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.models.rule import SearcherRule
from restweetution.twitter_client import TwitterClient
from restweetution.models.config.tweet_config import QueryFields
from restweetution.storages.storage import Storage
from restweetution.storage_manager import StorageManager


class Config(BaseModel):
    bearer_token: Optional[str]

    storages: Dict[str, Storage] = {}
    storage_list: List[Storage] = []

    storage_manager: Optional[StorageManager]
    storage_tags: Optional[dict] = []

    media_download: bool = True
    media_root_dir: str = None

    streamer: Optional[Streamer]
    streamer_rules: Optional[List[StreamRule]]
    streamer_verbose: Optional[bool]

    searcher: Optional[Searcher]
    searcher_rule: Optional[SearcherRule]

    query_fields: Optional[QueryFields]

    class Config:
        arbitrary_types_allowed = True
