from abc import ABC
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from restweetution.models.config.stream_query_params import ALL_CONFIG
from restweetution.models.config.tweet_config import QueryFields
from restweetution.models.searcher import TimeWindow


class RuleConfig(BaseModel):
    tag: str  # Tag that can be shared with other rules
    query: str  # Query string (streamer or searcher) Can also be used to describe custom rules


class CollectTasks(BaseModel):
    download_media: bool = False
    elastic_dashboard: bool = False
    elastic_dashboard_name: str = ''


class CollectorConfig(BaseModel, ABC):
    updated_at: datetime
    is_running: bool = False
    fields: QueryFields = ALL_CONFIG
    collect_tasks: CollectTasks = CollectTasks()

    def __init__(self, **kwargs):
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = datetime.now()
        super().__init__(**kwargs)

    def trigger_update(self):
        self.updated_at = datetime.now()


class StreamerConfig(CollectorConfig):
    rules: List[RuleConfig] = []


class SearcherConfig(CollectorConfig):
    rule: Optional[RuleConfig]
    time_window: TimeWindow() = TimeWindow()


class UserConfig(BaseModel):
    name: str = 'no name'
    bearer_token: str
    streamer_state: StreamerConfig
    searcher_state: SearcherConfig

    def __init__(self, bearer_token: str, **kwargs):
        if 'streamer_state' not in kwargs:
            kwargs['streamer_state'] = StreamerConfig()
        if 'searcher_state' not in kwargs:
            kwargs['searcher_state'] = SearcherConfig()

        super().__init__(bearer_token=bearer_token, **kwargs)
