import json
from typing import Optional, List, Dict, Union

import aiofiles
from pydantic import BaseModel
from tweepy import StreamRule

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.models.rule import SearcherRule, StreamerRule
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage
from restweetution.twitter_client import TwitterClient
from restweetution.models.config.tweet_config import QueryFields
from restweetution.storages.storage import Storage
from restweetution.storage_manager import StorageManager


class Config(BaseModel):
    persistent_path: Optional[str]
    bearer_token: Optional[str]

    storages: Dict[str, Union[Storage, PostgresStorage]] = {}
    storage_list: List[Storage] = []

    storage_manager: Optional[StorageManager]
    storage_tags: Optional[dict] = []

    media_download: bool = True
    media_root_dir: str = None

    streamer: Optional[Streamer]
    streamer_rules: Optional[List[StreamerRule]]
    streamer_verbose: Optional[bool]

    searcher: Optional[Searcher]
    searcher_rule: Optional[SearcherRule]

    query_fields: Optional[QueryFields]

    class Config:
        arbitrary_types_allowed = True

    async def write_config(self):
        async with aiofiles.open(self.persistent_path, 'w') as f:
            data = {'storages': [], 'streamer_rules': []}
            # for name, storage in self.storages.items():
            #     data['storages'].append(storage.get_config())
            for rule in self.streamer_rules:
                data['streamer_rules'].append(rule.get_config())
            await f.write(json.dumps(data, indent=4))

    async def read_persistent_config(self):
        async with aiofiles.open(self.persistent_path, 'r') as f:
            data = await f.read()
            if not data:
                return
            json_data = json.loads(data)

            self.streamer_rules = [StreamerRule(**rule) for rule in json_data['streamer_rules']]
            print(self.streamer_rules)

