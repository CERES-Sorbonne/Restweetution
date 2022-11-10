import json
from datetime import datetime
from typing import List, Optional, Set
from pydantic import BaseModel


class StreamAPIRule(BaseModel):
    id: str = 'unregistered'
    tag: str
    value: Optional[str]

    def hash(self):
        return hash(self.value)


class CollectedTweet(BaseModel):
    collected_at: datetime
    tweet_id: str


class Rule(BaseModel):
    id: Optional[int]  # database given
    type: str  # Storage, Searcher, Streamer
    tag: Optional[str]  # Tag that can be shared with other rules
    query: Optional[str]  # Query string (streamer or searcher) Can also be used to describe custom rules
    created_at: Optional[datetime]
    # tweet_ids: Set[str] = set()  # Set of collected tweet ids
    collected_tweets: List[CollectedTweet] = []

    def add_collected_tweets(self, tweet_ids, collected_at):
        for tweet_id in tweet_ids:
            self.collected_tweets.append(CollectedTweet(tweet_id=tweet_id, collected_at=collected_at))

    # def collected_ids(self):
    #     return [c.tweet_id for c in self.collected_tweets]

    def __init__(self, tag: str = None, **kwargs):
        if not tag:
            tag = 'default'
        super().__init__(tag=tag, **kwargs)

    def copy(self, **kwargs):
        return super().copy(deep=True, **kwargs)

    def __eq__(self, other):
        return self.type == other.type and self.tag == other.tag and self.query == other.query

    def __hash__(self):
        return hash((self.type, self.tag, self.query))

    def tag_query_hash(self):
        return hash((self.tag, self.query))

    def get_config(self):
        return {
            'id': self.id,
            'type': self.type,
            'tag': self.tag,
            'query': self.query
        }


class StreamerRule(Rule):
    api_id: Optional[str]

    def __init__(self, query: str, tag: str, name=None, **kwargs):
        name = f'Streamer_{tag}' if name is None else name
        if 'type' in kwargs:
            if kwargs['type'] != 'streamer':
                raise ValueError('Trying to initialize a StreamerRule of type ' + kwargs['type'])
            kwargs.pop('type')

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
