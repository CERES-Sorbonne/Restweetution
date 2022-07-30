from typing import List

from pydantic import BaseModel

from restweetution.models.bulk_data import BulkData


class BulkIds(BaseModel):
    rules: List[str] = []
    users: List[str] = []
    tweets: List[str] = []
    places: List[str] = []
    medias: List[str] = []
    polls: List[str] = []
    custom_datas: List[str] = []

    def add(self,
            rules: List[str] = [],
            users: List[str] = [],
            tweets: List[str] = [],
            places: List[str] = [],
            medias: List[str] = [],
            polls: List[str] = [],
            custom_datas: List[str] = []):
        self.rules.extend(rules)
        self.users.extend(users)
        self.tweets.extend(tweets)
        self.places.extend(places)
        self.medias.extend(medias)
        self.polls.extend(polls)
        self.custom_datas.extend(custom_datas)


class EventData(BaseModel):
    added: BulkIds = BulkIds()
    updated: BulkIds = BulkIds()
    delete: BulkIds = BulkIds()
    data: BulkData = BulkData()
