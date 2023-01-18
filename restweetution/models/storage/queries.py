from datetime import datetime
from typing import List

from pydantic import BaseModel


class TweetCountQuery(BaseModel):
    date_from: datetime = None
    date_to: datetime = None
    rule_ids: List[int] = None


class TweetQuery(TweetCountQuery):
    ids: List[str] = None
    offset: int = None
    limit: int = None
    order: int = 1
    tweet_fields: List[str] = None


class CollectedTweetQuery(TweetQuery):
    collected_fields: List[str] = None


class TweetRowQuery(CollectedTweetQuery):
    row_fields: List[str] = None
