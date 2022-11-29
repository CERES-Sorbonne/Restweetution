import json
from datetime import datetime
from typing import List, Optional, Set, Dict
from pydantic import BaseModel


class StreamAPIRule(BaseModel):
    id: str = 'unregistered'
    tag: str
    value: Optional[str]

    def hash(self):
        return hash(self.value)


class CollectedTweet(BaseModel):
    collected_at: datetime
    direct_hit: bool = False
    tweet_id: str
    rule_id: int

    def rule_tweet_id(self):
        return str(self.rule_id) + self.tweet_id


class Rule(BaseModel):
    id: Optional[int]  # database given
    type: str  # Storage, Searcher, Streamer
    tag: Optional[str]  # Tag that can be shared with other rules
    query: Optional[str]  # Query string (streamer or searcher) Can also be used to describe custom rules
    created_at: Optional[datetime]
    # tweet_ids: Set[str] = set()  # Set of collected tweet ids
    collected_tweets: Dict[str, CollectedTweet] = {}

    def config(self):
        return {"query": self.query, "tag": self.tag}

    def collected_tweets_list(self):
        return self.collected_tweets.values()

    def add_collected_tweets(self, tweet_ids, collected_at, direct_hit=False):
        for tweet_id in tweet_ids:
            collected = CollectedTweet(
                tweet_id=tweet_id,
                collected_at=collected_at,
                direct_hit=direct_hit,
                rule_id=self.id)
            if collected.rule_tweet_id() in self.collected_tweets:
                if direct_hit:
                    self.collected_tweets[collected.rule_tweet_id()].direct_hit = True
            else:
                self.collected_tweets[collected.rule_tweet_id()] = collected

    def add_direct_tweets(self, tweet_ids, collected_at):
        self.add_collected_tweets(tweet_ids, collected_at, direct_hit=True)

    def add_includes_tweets(self, tweet_ids, collected_at):
        self.add_collected_tweets(tweet_ids, collected_at, direct_hit=False)
    # def collected_ids(self):
    #     return [c.tweet_id for c in self.collected_tweets]

    def __init__(self, tag: str = None, **kwargs):
        if not tag:
            tag = 'default'
        # print(kwargs['collected_tweets'])
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

    def __init__(self, query: str, tag: str, **kwargs):
        if 'type' in kwargs:
            if kwargs['type'] != 'streamer':
                raise ValueError('Trying to initialize a StreamerRule of type ' + kwargs['type'])
            kwargs.pop('type')

        super().__init__(type='streamer', query=query, tag=tag, **kwargs)

    def get_api_rule(self):
        if self.api_id:
            return StreamAPIRule(tag=self.tag, value=self.query, id=self.api_id)
        else:
            return StreamAPIRule(tag=self.tag, value=self.query)


class SearcherRule(Rule):
    def __init__(self, query: str, tag: str, **kwargs):
        super().__init__(type='searcher', query=query, tag=tag, **kwargs)


class StorageRule(Rule):
    def __init__(self, tag: str, **kwargs):
        super().__init__(type='storage', tag=tag, **kwargs)


class DefaultRule(StorageRule):
    def __init__(self):
        super().__init__(tag='default')


class RuleResponseMeta(BaseModel):
    sent: str
    result_count: int


class StreamRuleResponse(BaseModel):
    data: List[StreamAPIRule]
    meta: RuleResponseMeta
