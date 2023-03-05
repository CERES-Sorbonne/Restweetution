from typing import Set, List

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

    def only_new_rules(self, ids: List[int]) -> List[int]:
        new_ids = [i for i in ids if i not in self.rules]
        return new_ids

    def only_new_users(self, ids: List[str]) -> List[str]:
        new_ids = [i for i in ids if i not in self.users]
        return new_ids

    def only_new_tweets(self, ids: List[str]) -> List[str]:
        new_ids = [i for i in ids if i not in self.tweets]
        return new_ids

    def only_new_places(self, ids: List[str]) -> List[str]:
        new_ids = [i for i in ids if i not in self.places]
        return new_ids

    def only_new_medias(self, ids: List[str]) -> List[str]:
        new_ids = [i for i in ids if i not in self.medias]
        return new_ids

    def only_new_polls(self, ids: List[str]) -> List[str]:
        new_ids = [i for i in ids if i not in self.polls]
        return new_ids


class EventData:
    def __init__(self):
        self.added: BulkIds = BulkIds()
        self.updated: BulkIds = BulkIds()
        self.delete: BulkIds = BulkIds()
        self.data: BulkData = BulkData()


