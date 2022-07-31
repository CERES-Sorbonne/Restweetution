import uuid
from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel

from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter import RestTweet, StreamRule


class CountUnit(BaseModel):
    start: datetime
    end: datetime
    tweet_count: int


class CountMeta(BaseModel):
    total_tweet_count: int


class CountResponse(BaseModel):
    data: List[CountUnit]
    meta: CountMeta
    includes: Dict = {}
    errors: List = []


class LookupResponseUnit(BaseModel):
    data: List
    includes: Dict
    errors: List
    meta: Dict
    requested_ids: List[str]
    missing_ids: List[str]


class LookupResponse(BaseModel):
    missing_ids: List[str] = []
    requested_ids: List[str] = []
    bulk_data: BulkData = BulkData()
    errors: List = []
    meta: Dict = {}

class DefaultSearcherRule(StreamRule):
    def __init__(self):
        super().__init__(id='searcher',)
