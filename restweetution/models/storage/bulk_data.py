from typing import List, Dict

from pydantic import BaseModel

from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.twitter import Media
from restweetution.models.storage.twitter.place import Place
from restweetution.models.storage.twitter import Poll
from restweetution.models.storage.stream_rule import StreamRule
from restweetution.models.storage.twitter.tweet import RestTweet
from restweetution.models.storage.twitter.user import User


class BulkData(BaseModel):
    rules: Dict[str, StreamRule] = {}
    users: Dict[str, User] = {}
    tweets: Dict[str, RestTweet] = {}
    places: Dict[str, Place] = {}
    medias: Dict[str, Media] = {}
    polls: Dict[str, Poll] = {}
    custom_datas: Dict[str, CustomData] = {}

    def __add__(self, other):
        self_dict = self.dict()
        other_dict = other.dict()

        for key1 in other_dict:
            if key1 == 'rules':
                for key2 in other_dict[key1]:
                    if key2 not in self_dict[key1]:
                        self_dict[key1][key2] = other_dict[key1][key2]
                    else:
                        self_dict[key1][key2]['tweet_ids'].extend(other_dict[key1][key2]['tweet_ids'])
            else:
                for key2 in other_dict[key1]:
                    self_dict[key1][key2] = other_dict[key1][key2]

        return BulkData(**self_dict)

    def add_rules(self, rules: List[StreamRule]):
        self.set_from_list(self.rules, rules)

    def add_tweets(self, tweets: List[RestTweet]):
        self.set_from_list(self.tweets, tweets)

    def add_users(self, users: List[User]):
        self.set_from_list(self.users, users)

    def add_places(self, places: List[Place]):
        self.set_from_list(self.places, places)

    def add_polls(self, polls: List[Poll]):
        self.set_from_list(self.polls, polls)

    def add_medias(self, medias: List[Media]):
        self.set_from_list(self.medias, medias, id_lambda=lambda m: m.media_key)

    def set_custom_datas(self, datas: List[CustomData]):
        self.set_from_list(self.custom_datas, datas, id_lambda=lambda d: d.unique_id())

    @staticmethod
    def set_from_list(target: dict, array: list, id_lambda=lambda x: x.id):
        for item in array:
            key = id_lambda(item)
            target[key] = item
