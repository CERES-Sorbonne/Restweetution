from datetime import datetime
from typing import List

from pydantic import BaseModel

from restweetution.models.view_types import ViewType


class TweetCountQuery(BaseModel):
    date_from: datetime = None
    date_to: datetime = None
    rule_ids: List[int] = None


class TweetQuery(TweetCountQuery):
    ids: List[str] = None
    offset: int = None
    limit: int = None
    order: int = 0
    tweet_fields: List[str] = None


class CollectedTweetQuery(TweetQuery):
    collected_fields: List[str] = None


class TweetRowQuery(CollectedTweetQuery):
    row_fields: List[str] = None


class CollectionCountQuery(BaseModel):
    date_from: datetime = None
    date_to: datetime = None
    rule_ids: List[int] = None
    direct_hit = False


class CollectionQuery(CollectionCountQuery):
    limit: int = None
    offset: int = None
    order: int = 1


class ViewQuery(BaseModel):
    collection: CollectionQuery
    view_type: ViewType


class TweetFilter(BaseModel):
    media: int = 0


class ExportQuery(BaseModel):
    key: str
    fields: List[str]
    query: ViewQuery
