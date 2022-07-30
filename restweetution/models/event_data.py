from typing import Set, Set

from pydantic import BaseModel

from restweetution.models.bulk_data import BulkData


class BulkIds(BaseModel):
    rules: Set[str] = set()
    users: Set[str] = set()
    tweets: Set[str] = set()
    places: Set[str] = set()
    medias: Set[str] = set()
    polls: Set[str] = set()
    custom_datas: Set[str] = set()

    def add(self,
            rules: Set[str] = set(),
            users: Set[str] = set(),
            tweets: Set[str] = set(),
            places: Set[str] = set(),
            medias: Set[str] = set(),
            polls: Set[str] = set(),
            custom_datas: Set[str] = set()):
        self.rules.update(rules)
        self.users.update(users)
        self.tweets.update(tweets)
        self.places.update(places)
        self.medias.update(medias)
        self.polls.update(polls)
        self.custom_datas.update(custom_datas)


class EventData(BaseModel):
    added: BulkIds = BulkIds()
    updated: BulkIds = BulkIds()
    delete: BulkIds = BulkIds()
    data: BulkData = BulkData()
