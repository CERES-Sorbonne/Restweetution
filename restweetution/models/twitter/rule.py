from typing import List, Optional, Set
from pydantic import BaseModel


class StreamAPIRule(BaseModel):
    id: str = 'unregistered'
    tag: str
    value: Optional[str]


class Rule(BaseModel):
    id: Optional[int]  # database given
    type: str  # Storage, Searcher, Streamer
    name: str  # User defined name for identification
    tag: Optional[str]  # Tag that can be shared with other rules
    query: Optional[str]  # Query string (streamer or searcher) Can also be used to describe custom rules

    tweet_ids: Set[str] = set()  # Set of collected tweet ids

    def __eq__(self, other):
        return self.type == other.type and self.tag == other.tag and self.query == other.query

    def __hash__(self):
        return hash((self.type, self.tag, self.query))


class StreamerRule(Rule):
    api_id: Optional[str]

    def __init__(self, query: str, tag: str, name=None, **kwargs):
        name = f'Streamer_{tag}' if name is None else name
        super().__init__(type='streamer', query=query, tag=tag, name=name, **kwargs)

    def get_api_rule(self):
        if self.api_id:
            return StreamAPIRule(tag=self.tag, value=self.query, id=self.api_id)
        else:
            return StreamAPIRule(tag=self.tag, value=self.query)


class SearcherRule(Rule):
    def __init__(self, query: str, tag: str, name=None, **kwargs):
        name = f'Searcher_{tag}' if name is None else name

        super().__init__(type='searcher', query=query, tag=tag, name=name, **kwargs)


class StorageRule(Rule):
    def __init__(self, tag: str, name=None, **kwargs):
        name = f'Storage_{tag}' if name is None else name

        super().__init__(type='storage', tag=tag, name=name, **kwargs)


class DefaultRule(StorageRule):
    def __init__(self):
        super().__init__(tag='default')


class RuleResponseMeta(BaseModel):
    sent: str
    result_count: int


class StreamRuleResponse(BaseModel):
    data: List[StreamAPIRule]
    meta: RuleResponseMeta
