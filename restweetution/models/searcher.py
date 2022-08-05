import uuid
from datetime import datetime
from typing import List, Dict, Set

from pydantic import BaseModel

from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter import RestTweet, StreamAPIRule


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
    requested: List[str]
    missing: Set[str]


class LookupResponse(BaseModel):
    missing: Set[str] = set()
    requested: List[str] = []
    bulk_data: BulkData = BulkData()
    errors: List = []
    meta: Dict = {}

    def __add__(self, other):
        self.missing.update(other.missing)
        self.requested.extend(other.requested)
        self.bulk_data += other.bulk_data
        self.errors.extend(other.errors)
        self.meta.update(other.meta)

        return self
