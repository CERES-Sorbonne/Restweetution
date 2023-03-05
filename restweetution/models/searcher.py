from datetime import datetime
from typing import List, Dict, Set, Optional

from pydantic import BaseModel

from restweetution.models.bulk_data import BulkData


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


class TweetPyLookupResponse(BaseModel):
    data: List[Dict] = []
    includes: Dict = {}
    errors: List[Dict] = []
    meta: Dict = {}


class LookupResponseUnit(BaseModel):
    data: List
    includes: Dict
    errors: List
    meta: Dict
    requested: List[str]
    missing: Set[str]


class LookupResponse:
    def __init__(self):
        self.missing: Set[str] = set()
        self.requested: List[str] = []
        self.bulk_data: BulkData = BulkData()
        self.errors: List = []
        self.meta: Dict = {}

    def __add__(self, other):
        self.missing.update(other.missing)
        self.requested.extend(other.requested)
        self.bulk_data += other.bulk_data
        self.errors.extend(other.errors)
        self.meta.update(other.meta)

        return self


class TimeWindow(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    cursor: Optional[datetime] = None

    recent: bool = True
    total_count: int = -1
    collected_count: int = 0

    def reset_counters(self):
        self.total_count = -1
        self.collected_count = 0

    def reset_cursor(self):
        self.reset_counters()
        self.cursor = None

    def has_count(self):
        return self.total_count != -1
