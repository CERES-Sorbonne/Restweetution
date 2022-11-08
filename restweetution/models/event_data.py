from typing import Set, Set

from pydantic import BaseModel

from restweetution.models.bulk_data import BulkData


class BulkIds(BaseModel):
    rules: Set[int] = set()
    users: Set[str] = set()
    tweets: Set[str] = set()
    places: Set[str] = set()
    medias: Set[str] = set()
    polls: Set[str] = set()
    custom_datas: Set[str] = set()

    def __add__(self, other):
        self.rules.update(other.rules)
        self.users.update(other.users)
        self.tweets.update(other.tweets)
        self.places.update(other.places)
        self.medias.update(other.medias)
        self.polls.update(other.polls)
        self.custom_datas.update(other.custom_datas)
        return self


class EventData(BaseModel):
    added: BulkIds = BulkIds()
    updated: BulkIds = BulkIds()
    delete: BulkIds = BulkIds()
    data: BulkData = BulkData()
