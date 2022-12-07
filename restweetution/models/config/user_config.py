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


class TaskConfig(BaseModel, ABC):
    updated_at: datetime
    is_running: bool = False
    fields: QueryFields = ALL_CONFIG

    def __init__(self, **kwargs):
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = datetime.now()
        super().__init__(**kwargs)

    def trigger_update(self):
        self.updated_at = datetime.now()


class StreamerTaskConfig(TaskConfig):
    rules: List[RuleConfig] = []


class SearcherTaskConfig(TaskConfig):
    rule: Optional[RuleConfig]
    time_window: TimeWindow() = TimeWindow()


class UserConfig(BaseModel):
    name: str = 'no name'
    bearer_token: str
    streamer_task_config: StreamerTaskConfig
    searcher_task_config: SearcherTaskConfig

    def __init__(self, bearer_token: str, **kwargs):
        if 'streamer_task_config' not in kwargs:
            kwargs['streamer_task_config'] = StreamerTaskConfig()
        if 'searcher_task_config' not in kwargs:
            kwargs['searcher_task_config'] = SearcherTaskConfig()

        super().__init__(bearer_token=bearer_token, **kwargs)
