from typing import List, Optional, Set
from pydantic import BaseModel


class RuleRef(BaseModel):
    id: str
    tag: str


class StreamRule(RuleRef):
    value: Optional[str]
    tweet_ids: Optional[Set[str]] = set()

    def get_tweet_ids(self):
        return list(self.tweet_ids)


class RuleResponseMeta(BaseModel):
    sent: str
    result_count: int


class RuleResponse(BaseModel):
    data: List[StreamRule]
    meta: RuleResponseMeta
