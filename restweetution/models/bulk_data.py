from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel

from restweetution.models.storage.custom_data import CustomData
from restweetution.models.twitter import Media
from restweetution.models.twitter.place import Place
from restweetution.models.twitter import Poll
from restweetution.models.rule import Rule
from restweetution.models.twitter.tweet import RestTweet
from restweetution.models.twitter.user import User


class BulkData(BaseModel):
    rules: Dict[int, Rule] = {}
    users: Dict[str, User] = {}
    tweets: Dict[str, RestTweet] = {}
    places: Dict[str, Place] = {}
    medias: Dict[str, Media] = {}
    polls: Dict[str, Poll] = {}
    custom_datas: Dict[str, CustomData] = {}
    timestamp: datetime = None

    def __add__(self, other):
        for k in other.tweets:
            self.tweets[k] = other.tweets[k]
        for k in other.users:
            self.users[k] = other.users[k]
        for k in other.places:
            self.places[k] = other.places[k]
        for k in other.medias:
            self.medias[k] = other.medias[k]
        for k in other.polls:
            self.polls[k] = other.polls[k]
        for k in other.custom_datas:
            self.custom_datas[k] = other.custom_datas[k]
        for k in other.rules:
            if k not in self.rules:
                self.rules[k] = other.rules[k]
            else:
                self.rules[k].tweet_ids.update(other.rules[k].tweet_ids)
        return self

    def copy(self, **kwargs):
        other = BulkData()
        other.tweets = self.tweets.copy()
        other.users = self.users.copy()
        other.medias = self.medias.copy()
        other.rules = self.rules.copy()
        other.polls = self.polls.copy()
        other.places = self.places.copy()
        other.custom_datas = self.custom_datas.copy()

        return other

    def add(self,
            tweets: List[RestTweet] = [],
            users: List[User] = [],
            medias: List[Media] = [],
            places: List[Place] = [],
            polls: List[Poll] = [],
            rules: List[Rule] = [],
            datas: List[CustomData] = []):
        self.add_tweets(tweets)
        self.add_users(users)
        self.add_places(places)
        self.add_medias(medias)
        self.add_polls(polls)
        self.add_rules(rules)
        self.add_datas(datas)

    def add_rules(self, rules: List[Rule], collected=False):
        for rule in rules:
            if collected:
                rule.tweet_ids.update(self.tweets.keys())
            if rule.id not in self.rules:
                self.rules[rule.id] = rule
            else:
                self.rules[rule.id].tweet_ids.update(rule.tweet_ids)

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

    def add_datas(self, datas: List[CustomData]):
        self.set_from_list(self.custom_datas, datas, id_lambda=lambda d: d.unique_id())

    def get_tweets(self):
        return list(self.tweets.values())

    def get_rules(self):
        return list(self.rules.values())

    def get_users(self):
        return list(self.users.values())

    def get_medias(self):
        return list(self.medias.values())

    def get_polls(self):
        return list(self.polls.values())

    def get_places(self):
        return list(self.places.values())

    @staticmethod
    def set_from_list(target: dict, array: list, id_lambda=lambda x: x.id):
        for item in array:
            key = id_lambda(item)
            target[key] = item
