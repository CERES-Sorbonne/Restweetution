from typing import Optional, List, Dict

from pydantic import BaseModel

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.media_downloader import MediaDownloader
from restweetution.models.config.tweet_config import QueryFields
from restweetution.models.rule import SearcherRule, StreamerRule
from restweetution.storages.exporter.exporter import Exporter
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage


class Config(BaseModel):
    bearer_token: Optional[str]

    storage: Optional[PostgresStorage]

    exporters: Optional[Dict[str, Exporter]] = {}

    media_downloader: Optional[MediaDownloader]
    media_download_active: bool = True
    media_root_dir: str = None

    streamer: Optional[Streamer]
    streamer_rules: Optional[List[StreamerRule]]
    streamer_verbose: Optional[bool]

    searcher: Optional[Searcher]
    searcher_rule: Optional[SearcherRule]

    query_fields: Optional[QueryFields]

    class Config:
        arbitrary_types_allowed = True

    # async def write_config(self):
    #     async with aiofiles.open(self.persistent_path, 'w') as f:
    #         data = {'storages': [], 'streamer_rules': []}
    #         # for name, storage in self.storages.items():
    #         #     data['storages'].append(storage.get_config())
    #         for rule in self.streamer_rules:
    #             data['streamer_rules'].append(rule.get_config())
    #         await f.write(json.dumps(data, indent=4))
    #
    # async def read_persistent_config(self):
    #     async with aiofiles.open(self.persistent_path, 'r') as f:
    #         data = await f.read()
    #         if not data:
    #             return
    #         json_data = json.loads(data)
    #
    #         self.streamer_rules = [StreamerRule(**rule) for rule in json_data['streamer_rules']]
    #         print(self.streamer_rules)

